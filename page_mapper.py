import re


def normalize_text(text):
    return re.sub(r"\s+", " ", text.lower()).strip()


def find_last_toc_page(pages):
    """
    Finds the last PDF page that appears to belong to the table of contents.
    """

    last_toc_page = 0

    for page in pages:
        page_text = normalize_text(page["text"])

        if "contents" in page_text[:300]:
            last_toc_page = page["page_number"]

        if "chapter 1" in page_text and "chapter 2" in page_text:
            last_toc_page = page["page_number"]

    return last_toc_page


def detect_page_offset(pages, first_chapter):
    """
    Detects offset between textbook page numbers and PDF page numbers.
    """

    chapter_number = first_chapter["chapter_number"]
    chapter_title = normalize_text(first_chapter["chapter_title"])
    textbook_start_page = first_chapter["start_page"]

    last_toc_page = find_last_toc_page(pages)

    title_words = [
        word for word in chapter_title.split()
        if len(word) > 3
    ]

    for page in pages:
        pdf_page_number = page["page_number"]

        if pdf_page_number <= last_toc_page:
            continue

        page_text = normalize_text(page["text"])

        word_match_count = sum(
            1 for word in title_words
            if word in page_text
        )

        enough_title_words = word_match_count >= max(
            2,
            len(title_words) - 1
        )

        has_chapter_number = re.search(
            rf"(^|\s){chapter_number}(\s|$)",
            page_text
        )

        if enough_title_words and has_chapter_number:
            return pdf_page_number - textbook_start_page

    return 0
