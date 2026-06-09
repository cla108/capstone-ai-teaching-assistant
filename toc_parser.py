
import re


def extract_toc_lines(full_text, max_toc_pages=20):
    """
    Extracts raw Table of Contents (TOC) lines from the full textbook text.

    Stops after a limited number of TOC pages to avoid reading the whole book.
    """

    lines = full_text.splitlines()

    toc_lines = []
    inside_toc = False
    toc_start_pdf_page = None
    current_pdf_page = None

    for line in lines:
        clean = line.strip()

        page_match = re.match(r"--- PAGE (\d+) ---", clean)

        if page_match:
            current_pdf_page = int(page_match.group(1))

            if inside_toc and toc_start_pdf_page is not None:
                if current_pdf_page > toc_start_pdf_page + max_toc_pages:
                    break

            continue

        if clean.lower() in ["contents", "table of contents"]:
            inside_toc = True
            toc_start_pdf_page = current_pdf_page
            continue

        if inside_toc:
            if not clean:
                continue

            if clean.lower().startswith("preface"):
                continue

            toc_lines.append(clean)

    return toc_lines


def is_noise_line(line):
    """
    Checks whether a TOC line is noise rather than useful structure.

    Parameters:
        line (str):
            A single extracted TOC line.

    Returns:
        bool:
            True if the line is noise; False otherwise.

    Purpose:
        Removes PDF artifacts such as Roman numeral page labels
        and repeated 'Contents' headers.
    """

    line = line.strip()

    noise_patterns = [
        r"^[ivxlcdm]+$",
        r"^[ivxlcdm]+\s+Contents$",
        r"^Contents\s+[ivxlcdm]+$",
    ]

    for pattern in noise_patterns:
        if re.match(pattern, line, re.IGNORECASE):
            return True

    return False


def normalize_toc_lines(toc_lines):
    """
    Normalizes raw TOC lines into complete TOC entries.

    Parameters:
        toc_lines (list[str]):
            Raw TOC lines extracted from the textbook.

    Returns:
        list[str]:
            Cleaned and merged TOC entries.

    Purpose:
        Fixes common PDF extraction issues, especially multiline entries.
        For example:

            Chapter 3 Transportation Regulation and Public
            Policy 54

        becomes:

            Chapter 3 Transportation Regulation and Public Policy 54

    Notes:
        A TOC entry is considered complete when it ends with a page number.
        Part headings are preserved even though they usually do not have
        page numbers.
    """

    entries = []
    buffer = ""

    for raw_line in toc_lines:
        line = raw_line.strip()

        if is_noise_line(line):
            continue

        if re.match(r"^Part\s+[IVXLC]+$", line, re.IGNORECASE):
            if buffer:
                entries.append(buffer.strip())
                buffer = ""

            entries.append(line)
            continue

        if re.match(r"^Chapter\s+\d+\b", line, re.IGNORECASE):
            if buffer:
                entries.append(buffer.strip())
                buffer = ""

            buffer = line

            if re.search(r"\s\d+$", buffer):
                entries.append(buffer.strip())
                buffer = ""

            continue

        if not buffer:
            buffer = line
        else:
            buffer += " " + line

        if re.search(r"\s\d+$", buffer):
            entries.append(buffer.strip())
            buffer = ""

    if buffer:
        entries.append(buffer.strip())

    return entries


def parse_toc(toc_lines):
    """
    Parses normalized TOC entries into a structured textbook hierarchy.

    Parameters:
        toc_lines (list[str]):
            Raw TOC lines extracted from the textbook.

    Returns:
        list[dict]:
            Structured representation of the textbook.

            Example:
            [
                {
                    "part": "Part I",
                    "chapters": [
                        {
                            "chapter_number": 1,
                            "chapter_title": "...",
                            "start_page": 3,
                            "sections": [
                                {
                                    "section_title": "...",
                                    "start_page": 6
                                }
                            ]
                        }
                    ]
                }
            ]

    Purpose:
        Converts the Table of Contents into machine-readable metadata
        that can be used for chapter extraction, section-aware chunking,
        RAG retrieval, citation tracing, and lesson-plan generation.
    """

    entries = normalize_toc_lines(toc_lines)

    structure = []
    current_part = None
    current_chapter = None

    part_pattern = re.compile(r"^Part\s+([IVXLC]+)\s*(.*)$", re.IGNORECASE)
    chapter_pattern = re.compile(
        r"^Chapter\s+(\d+)\s+(.+?)\s+(\d+)$",
        re.IGNORECASE
    )
    section_pattern = re.compile(r"^(.+?)\s+(\d+)$")

    ignored_starts = (
        "Preface",
        "About the Authors",
        "Suggested Readings",
        "Glossary",
        "Name Index",
        "Subject Index",
        "Appendix A",
        "Appendix B",
    )

    for entry in entries:
        part_match = part_pattern.match(entry)

        if part_match:
            current_part = {
                "part": entry,
                "chapters": []
            }
            structure.append(current_part)
            current_chapter = None
            continue

        if entry.startswith(ignored_starts):
            current_chapter = None
            continue




        chapter_match = chapter_pattern.match(entry)





        if chapter_match:
            chapter_title = chapter_match.group(2).strip()
            chapter_number = int(chapter_match.group(1))
            start_page = int(chapter_match.group(3))

            # Ignore running headers / repeated chapter titles
            if chapter_title.startswith("•"):
                continue

            # Ignore duplicate chapter numbers after the first valid occurrence
            existing_chapter_numbers = [
                chapter["chapter_number"]
                for part in structure
                for chapter in part["chapters"]
            ]

            if chapter_number in existing_chapter_numbers:
                continue

            current_chapter = {
                "chapter_number": chapter_number,
                "chapter_title": chapter_title,
                "start_page": start_page,
                "sections": []
            }







            if current_part is None:
                current_part = {
                    "part": "No Part",
                    "chapters": []
                }
                structure.append(current_part)

            current_part["chapters"].append(current_chapter)
            continue

        section_match = section_pattern.match(entry)

        if section_match and current_chapter is not None:
            current_chapter["sections"].append({
                "section_title": section_match.group(1).strip(),
                "start_page": int(section_match.group(2))
            })

    return structure
