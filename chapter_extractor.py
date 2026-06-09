from page_mapper import detect_page_offset


def flatten_chapters(structure):
    """
    Converts nested TOC structure into a flat chapter list.
    """

    chapters = []

    for part in structure:
        for chapter in part["chapters"]:
            chapters.append({
                "part": part["part"],
                "chapter_number": chapter["chapter_number"],
                "chapter_title": chapter["chapter_title"],
                "start_page": chapter["start_page"],
                "sections": chapter["sections"]
            })

    return chapters


def extract_chapters_from_pages(pages, structure):
    """
    Extracts full chapter text using chapter start pages from the parsed TOC.
    Automatically maps textbook page numbers to PDF page numbers.
    """

    flat_chapters = flatten_chapters(structure)
    extracted_chapters = []

    if not flat_chapters:
        return extracted_chapters

    page_offset = detect_page_offset(pages, flat_chapters[0])

    for i, chapter in enumerate(flat_chapters):
        textbook_start_page = chapter["start_page"]

        if i + 1 < len(flat_chapters):
            textbook_end_page = flat_chapters[i + 1]["start_page"] - 1
        else:
            textbook_end_page = pages[-1]["page_number"] - page_offset

        pdf_start_page = textbook_start_page + page_offset
        pdf_end_page = textbook_end_page + page_offset

        chapter_pages = [
            page for page in pages
            if pdf_start_page <= page["page_number"] <= pdf_end_page
        ]

        chapter_text = ""

        for page in chapter_pages:
            chapter_text += f"\n--- PDF PAGE {page['page_number']} ---\n"
            chapter_text += page["text"]

        extracted_chapters.append({
            "part": chapter["part"],
            "chapter_number": chapter["chapter_number"],
            "chapter_title": chapter["chapter_title"],

            "start_page": textbook_start_page,
            "end_page": textbook_end_page,

            "pdf_start_page": pdf_start_page,
            "pdf_end_page": pdf_end_page,
            "page_offset": page_offset,

            "sections": chapter["sections"],
            "text": chapter_text.strip()
        })

    return extracted_chapters
