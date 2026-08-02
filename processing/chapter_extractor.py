"""
Chapter extraction utilities.

This version aligns printed textbook page numbers with physical PDF pages
before extracting chapter text. The alignment prevents a selected chapter
from accidentally including pages from the preceding chapter.
"""

from __future__ import annotations

from collections import Counter
import re
from statistics import median
from typing import Any, Optional, Sequence

from processing.chapter_metadata import (
    flatten_chapters,
    build_chapter_ranges,
)


_ALIGNMENT_SEARCH_RADIUS = 6
_MIN_ALIGNMENT_SCORE = 7.0


def _page_text(page: Any) -> str:
    if isinstance(page, dict):
        return str(page.get("text", "") or "")
    return str(page or "")


def _normalize(text: str) -> str:
    text = str(text or "").casefold()
    text = text.replace("\u00a0", " ")
    text = text.replace("\u2013", "-")
    text = text.replace("\u2014", "-")
    text = re.sub(r"-\s*\n\s*", "", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _lines(text: str) -> list[str]:
    return [
        re.sub(r"\s+", " ", line).strip()
        for line in str(text or "").splitlines()
        if line.strip()
    ]


def _looks_like_contents_page(text: str) -> bool:
    lines = _lines(text)
    if not lines:
        return False

    first_text = " ".join(lines[:25]).casefold()

    if "table of contents" in first_text:
        return True

    contents_heading = any(
        re.fullmatch(r"(?:table of )?contents", line, re.IGNORECASE)
        for line in lines[:12]
    )

    chapter_entries = sum(
        1
        for line in lines[:100]
        if re.match(
            r"^\s*chapter\s+[a-z0-9]+\s+.+\s+\d{1,4}\s*$",
            line,
            re.IGNORECASE,
        )
    )

    numbered_entries = sum(
        1
        for line in lines[:100]
        if re.match(
            r"^\s*\d+(?:\.\d+)+\s+.+\s+\d{1,4}\s*$",
            line,
        )
    )

    dotted_entries = sum(
        1
        for line in lines[:100]
        if re.search(r"\.{2,}\s*\d{1,4}\s*$", line)
    )

    return (
        contents_heading
        or chapter_entries >= 3
        or numbered_entries >= 5
        or dotted_entries >= 5
    )


def _significant_title_tokens(title: str) -> set[str]:
    stop_words = {
        "a", "an", "and", "as", "at", "by", "for", "from", "in",
        "of", "on", "or", "the", "to", "with",
    }

    return {
        token
        for token in _normalize(title).split()
        if len(token) >= 3 and token not in stop_words
    }


def _title_line_position(lines: Sequence[str], title_tokens: set[str]) -> Optional[int]:
    if not title_tokens:
        return None

    for index, line in enumerate(lines[:80]):
        line_tokens = set(_normalize(line).split())

        if not line_tokens:
            continue

        overlap = len(title_tokens & line_tokens) / len(title_tokens)

        if overlap >= 0.55:
            return index

    return None


def _chapter_number_signals(
    lines: Sequence[str],
    chapter_number: str,
) -> tuple[bool, bool]:
    number = re.escape(str(chapter_number).strip())
    first_lines = lines[:25]

    explicit = any(
        re.search(
            rf"\bchapter\s+{number}\b",
            line,
            re.IGNORECASE,
        )
        for line in first_lines
    )

    standalone = any(
        re.fullmatch(
            rf"{number}",
            line.strip(),
            re.IGNORECASE,
        )
        for line in first_lines[:12]
    )

    return explicit, standalone


def _score_page_for_chapter(
    page_text: str,
    chapter: dict,
    *,
    expected_pdf_page: Optional[int] = None,
    physical_pdf_page: Optional[int] = None,
) -> float:
    """Score how likely one physical PDF page is to be a chapter opening."""

    if not page_text.strip():
        return float("-inf")

    title = str(chapter.get("chapter_title", "") or "").strip()
    number = str(chapter.get("chapter_number", "") or "").strip()

    if not title or not number:
        return float("-inf")

    lines = _lines(page_text)
    top_lines = lines[:80]

    top_text = _normalize("\n".join(top_lines))
    full_text = _normalize(page_text)
    title_normalized = _normalize(title)
    title_tokens = _significant_title_tokens(title)

    score = 0.0

    if title_normalized and title_normalized in top_text:
        score += 10.0
    elif title_normalized and title_normalized in full_text:
        score += 3.0

    top_tokens = set(top_text.split())

    if title_tokens:
        coverage = len(title_tokens & top_tokens) / len(title_tokens)
        score += coverage * 7.0

    position = _title_line_position(top_lines, title_tokens)

    if position is not None:
        if position <= 8:
            score += 4.0
        elif position <= 20:
            score += 2.0
        elif position > 45:
            score -= 2.0

    explicit_number, standalone_number = _chapter_number_signals(
        top_lines,
        number,
    )

    if explicit_number:
        score += 5.0

    if standalone_number:
        score += 4.0

    beginning = "\n".join(top_lines).casefold()

    if re.search(r"\blearning\s+objectives?\b", beginning):
        score += 5.0

    if re.search(r"\blearning\s+outcomes?\b", beginning):
        score += 4.0

    if re.search(r"\bchapter\s+(?:overview|introduction)\b", beginning):
        score += 3.0

    if _looks_like_contents_page(page_text):
        score -= 22.0

    if expected_pdf_page is not None and physical_pdf_page is not None:
        distance = abs(physical_pdf_page - expected_pdf_page)
        score -= min(distance * 0.35, 8.0)

    return score


def _find_best_page(
    pages: Sequence[Any],
    chapter: dict,
    *,
    expected_pdf_page: Optional[int] = None,
    radius: Optional[int] = None,
) -> tuple[Optional[int], float]:
    """Return the best 1-based physical PDF page for one chapter."""

    total_pages = len(pages)

    if total_pages == 0:
        return None, float("-inf")

    if expected_pdf_page is not None and radius is not None:
        start = max(1, expected_pdf_page - radius)
        end = min(total_pages, expected_pdf_page + radius)
    else:
        start = 1
        end = total_pages

    best_page: Optional[int] = None
    best_score = float("-inf")

    for pdf_page in range(start, end + 1):
        score = _score_page_for_chapter(
            _page_text(pages[pdf_page - 1]),
            chapter,
            expected_pdf_page=expected_pdf_page,
            physical_pdf_page=pdf_page,
        )

        if score > best_score:
            best_page = pdf_page
            best_score = score

    return best_page, best_score


def _as_positive_int(value: Any) -> Optional[int]:
    try:
        result = int(value)
    except (TypeError, ValueError):
        return None

    return result if result > 0 else None


def _infer_printed_to_pdf_offset(
    pages: Sequence[Any],
    chapters: Sequence[dict],
) -> int:
    """
    Infer the global difference:

        physical PDF page = printed page + offset
    """

    offsets: list[int] = []

    for chapter in list(chapters)[:8]:
        printed_start = _as_positive_int(chapter.get("start_page"))

        if printed_start is None:
            continue

        best_page, score = _find_best_page(
            pages,
            chapter,
        )

        if best_page is None or score < _MIN_ALIGNMENT_SCORE:
            continue

        offsets.append(best_page - printed_start)

    if not offsets:
        return 0

    counts = Counter(offsets)
    most_common_offset, most_common_count = counts.most_common(1)[0]

    if most_common_count >= 2:
        return int(most_common_offset)

    return int(round(median(offsets)))


def _resolve_chapter_starts(
    pages: Sequence[Any],
    chapters: Sequence[dict],
    offset: int,
) -> list[tuple[int, float, str]]:
    """Resolve one physical start page per chapter."""

    total_pages = len(pages)
    resolved: list[tuple[int, float, str]] = []
    previous_start = 0

    for chapter in chapters:
        printed_start = _as_positive_int(chapter.get("start_page"))

        if printed_start is None:
            expected = previous_start + 1
        else:
            expected = printed_start + offset

        expected = max(1, min(expected, total_pages))

        best_page, best_score = _find_best_page(
            pages,
            chapter,
            expected_pdf_page=expected,
            radius=_ALIGNMENT_SEARCH_RADIUS,
        )

        if best_page is not None and best_score >= _MIN_ALIGNMENT_SCORE:
            candidate = best_page
            method = "title-aligned"
        else:
            candidate = expected
            best_score = 0.0
            method = "offset-fallback"

        if candidate <= previous_start:
            candidate = min(total_pages, previous_start + 1)
            method = f"{method}+sequence-corrected"

        resolved.append((candidate, best_score, method))
        previous_start = candidate

    return resolved


def extract_chapters_from_pages(pages, toc_structure):
    """
    Extract the text for every chapter.

    The TOC supplies printed page numbers. This function determines the
    printed-to-PDF page offset and verifies each chapter opening against its
    title. End pages are based on the next verified chapter start.
    """

    chapters = flatten_chapters(toc_structure)
    chapters = build_chapter_ranges(chapters)

    if not pages or not chapters:
        return []

    total_pages = len(pages)
    offset = _infer_printed_to_pdf_offset(pages, chapters)

    resolved_starts = _resolve_chapter_starts(
        pages,
        chapters,
        offset,
    )

    extracted = []

    for index, chapter in enumerate(chapters):
        pdf_start_page, alignment_score, alignment_method = resolved_starts[index]

        if index + 1 < len(resolved_starts):
            next_pdf_start = resolved_starts[index + 1][0]
            pdf_end_page = max(
                pdf_start_page,
                next_pdf_start - 1,
            )
        else:
            pdf_end_page = total_pages

        chapter_text = "\n\n".join(
            _page_text(page)
            for page in pages[pdf_start_page - 1:pdf_end_page]
        ).strip()

        extracted.append(
            {
                "part": chapter.get("part"),
                "chapter_number": chapter["chapter_number"],
                "chapter_title": chapter["chapter_title"],
                "start_page": chapter.get("start_page"),
                "end_page": chapter.get("end_page"),
                "pdf_start_page": pdf_start_page,
                "pdf_end_page": pdf_end_page,
                "sections": chapter.get("sections", []),
                "page_offset": offset,
                "page_alignment_method": alignment_method,
                "page_alignment_score": round(alignment_score, 3),
                "text": chapter_text,
            }
        )

    return extracted
