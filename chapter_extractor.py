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
    """

    flat_chapters = flatten_chapters(structure)
    extracted_chapters = []

    for i, chapter in enumerate(flat_chapters):
        start_page = chapter["start_page"]

        if i + 1 < len(flat_chapters):
            end_page = flat_chapters[i + 1]["start_page"] - 1
        else:
            end_page = pages[-1]["page_number"]

        chapter_pages = [
            page for page in pages
            if start_page <= page["page_number"] <= end_page
        ]

        chapter_text = ""

        for page in chapter_pages:
            chapter_text += f"\n--- PAGE {page['page_number']} ---\n"
            chapter_text += page["text"]

        extracted_chapters.append({
            "part": chapter["part"],
            "chapter_number": chapter["chapter_number"],
            "chapter_title": chapter["chapter_title"],
            "start_page": start_page,
            "end_page": end_page,
            "sections": chapter["sections"],
            "text": chapter_text.strip()
        })

    return extracted_chapters
