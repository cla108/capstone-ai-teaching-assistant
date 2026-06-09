from pdf_processor import extract_text_from_pdf, combine_pages
from toc_parser import extract_toc_lines, normalize_toc_lines, parse_toc
from chapter_extractor import flatten_chapters, extract_chapters_from_pages

PDF_PATH = input("PDF path: ").strip()

pages = extract_text_from_pdf(PDF_PATH)
full_text = combine_pages(pages)

toc_lines = extract_toc_lines(full_text)
normalized_entries = normalize_toc_lines(toc_lines)
structure = parse_toc(toc_lines)

flat_chapters = flatten_chapters(structure)
chapters = extract_chapters_from_pages(pages, structure)

print("\n--- PDF SUMMARY ---")
print("Pages:", len(pages))
print("TOC lines:", len(toc_lines))
print("Normalized entries:", len(normalized_entries))
print("Flat chapters:", len(flat_chapters))
print("Extracted chapters:", len(chapters))

print("\n--- FLAT CHAPTERS ---")
for ch in flat_chapters:
    print(
        f"Chapter {ch['chapter_number']} | "
        f"{ch['chapter_title']} | "
        f"textbook page {ch['start_page']}"
    )

print("\n--- EXTRACTED CHAPTERS ---")
for ch in chapters:
    print(
        f"Chapter {ch['chapter_number']} | "
        f"{ch['chapter_title']} | "
        f"textbook {ch['start_page']}-{ch['end_page']} | "
        f"pdf {ch.get('pdf_start_page')}-{ch.get('pdf_end_page')} | "
        f"offset {ch.get('page_offset')}"
    )
