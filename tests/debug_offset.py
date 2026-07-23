from processing.pdf_processor import extract_text_from_pdf

PDF_PATH = input("PDF path: ").strip()

pages = extract_text_from_pdf(PDF_PATH)

search_terms = [
    "UNDERSTANDING THE SUPPLY CHAIN",
    "Chapter 1",
    "1 UNDERSTANDING THE SUPPLY CHAIN"
]

for page in pages:
    text = page["text"]

    for term in search_terms:
        if term.lower() in text.lower():
            print("\n--- MATCH ---")
            print("PDF page:", page["page_number"])
            print("Matched term:", term)
            print(text[:1000])
            break
