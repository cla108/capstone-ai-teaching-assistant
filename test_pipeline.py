from pdf_processor import extract_text_from_pdf, combine_pages
from toc_parser import extract_toc_lines, parse_toc

from chapter_splitter import (
    flatten_chapters,
    add_chapter_end_pages,
    apply_page_offset,
    extract_all_chapters_text
)

PDF_PATH = "Chopra_Meindl_SCM.pdf"
PAGE_OFFSET = 13


pages = extract_text_from_pdf(PDF_PATH)

full_text = combine_pages(pages)

toc_lines = extract_toc_lines(full_text)

structure = parse_toc(toc_lines)

chapters = flatten_chapters(structure)

chapters = add_chapter_end_pages(chapters)

chapters = apply_page_offset(
    chapters,
    offset=PAGE_OFFSET
)

chapters_with_text = extract_all_chapters_text(
    pages,
    chapters
)

for chapter in chapters_with_text[:5]:
    print(
        chapter["chapter_number"],
        chapter["chapter_title"],
        chapter["pdf_start_page"],
        chapter["pdf_end_page"],
        len(chapter["text"])
    )
