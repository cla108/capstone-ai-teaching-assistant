import pypdfium2 as pdfium


def extract_text_from_pdf(pdf_file):
    pdf = pdfium.PdfDocument(pdf_file)

    pages = []

    for page_index in range(len(pdf)):
        page = pdf[page_index]
        textpage = page.get_textpage()
        text = textpage.get_text_range()

        pages.append({
            "page_number": page_index + 1,
            "text": text
        })

    return pages


def combine_pages(pages):
    full_text = ""

    for page in pages:
        full_text += f"\n--- PAGE {page['page_number']} ---\n"
        full_text += page["text"]

    return full_text
