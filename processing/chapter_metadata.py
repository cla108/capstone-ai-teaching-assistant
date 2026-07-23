def flatten_chapters(structure):
    """
    Flatten the nested TOC into a simple chapter list.
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


def build_chapter_ranges(chapters):
    """
    Add end pages to every chapter.
    """

    results = []

    for i, chapter in enumerate(chapters):

        ch = chapter.copy()

        if i < len(chapters) - 1:
            ch["end_page"] = chapters[i + 1]["start_page"] - 1
        else:
            ch["end_page"] = None

        results.append(ch)

    return results
