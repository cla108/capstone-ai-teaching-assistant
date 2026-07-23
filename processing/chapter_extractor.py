"""
Chapter extraction utilities.

This module is responsible for extracting the full text belonging to each
chapter after the table of contents has been parsed.

Responsibilities
----------------
- Determine the page range for each chapter.
- Concatenate the pages belonging to that chapter.
- Return chapter dictionaries ready for chunking.
"""

from processing.chapter_metadata import (
    flatten_chapters,
    build_chapter_ranges,
)


def extract_chapters_from_pages(pages, toc_structure):
    """
    Extract the text for every chapter.

    Parameters
    ----------
    pages : list[str]
        List containing the extracted text of every PDF page.

    toc_structure : list
        Parsed table of contents.

    Returns
    -------
    list[dict]
        One dictionary per chapter.

        {
            "part": "...",
            "chapter_number": "...",
            "chapter_title": "...",
            "start_page": int,
            "end_page": int,
            "pdf_start_page": int,
            "pdf_end_page": int,
            "sections": [...],
            "text": "..."
        }
    """

    chapters = flatten_chapters(toc_structure)
    chapters = build_chapter_ranges(chapters)

    total_pages = len(pages)

    extracted = []

    for chapter in chapters:

        # TOC page numbers usually start at 1.
        pdf_start = max(chapter["start_page"] - 1, 0)

        if chapter["end_page"] is None:
            pdf_end = total_pages - 1
        else:
            pdf_end = min(chapter["end_page"] - 1, total_pages - 1)

        chapter_text = "\n\n".join(
            page["text"]
            for page in pages[pdf_start:pdf_end + 1]
        ).strip()

        extracted.append(
            {
                "part": chapter.get("part"),

                "chapter_number": chapter["chapter_number"],

                "chapter_title": chapter["chapter_title"],

                "start_page": chapter["start_page"],

                "end_page": chapter["end_page"],

                "pdf_start_page": pdf_start + 1,

                "pdf_end_page": pdf_end + 1,

                "sections": chapter.get("sections", []),

                "text": chapter_text,
            }
        )

    return extracted
