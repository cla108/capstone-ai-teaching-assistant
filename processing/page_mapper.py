def apply_page_offset(chapters, offset):
    """
    Convert textbook page numbers to PDF page numbers.
    """

    adjusted = []

    for chapter in chapters:

        ch = chapter.copy()

        ch["pdf_start_page"] = chapter["start_page"] + offset

        if chapter["end_page"] is None:
            ch["pdf_end_page"] = None
        else:
            ch["pdf_end_page"] = chapter["end_page"] + offset

        adjusted.append(ch)

    return adjusted


def apply_page_offset(chapters, offset):
    """
    Convert textbook page numbers into PDF page numbers.

    Parameters
    ----------
    chapters : list
        Chapter list containing textbook page numbers.

    offset : int
        Difference between textbook numbering and PDF indexing.

    Returns
    -------
    list
        Chapter list including:
        - pdf_start_page
        - pdf_end_page
    """

    adjusted_chapters = []

    for chapter in chapters:
        chapter_copy = chapter.copy()

        chapter_copy["pdf_start_page"] = chapter["start_page"] + offset

        if chapter["end_page"] is not None:
            chapter_copy["pdf_end_page"] = chapter["end_page"] + offset
        else:
            chapter_copy["pdf_end_page"] = None

        adjusted_chapters.append(chapter_copy)

    return adjusted_chapters
