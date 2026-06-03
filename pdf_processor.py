from io import BytesIO

import pypdfium2 as pdfium


def extract_text_from_pdf(pdf_file):
    """
    Extracts raw text from each page of a PDF document.
    """

    if hasattr(pdf_file, "getvalue"):
        pdf_bytes = pdf_file.getvalue()
        pdf_input = BytesIO(pdf_bytes)
    else:
        pdf_input = pdf_file

    pdf = pdfium.PdfDocument(pdf_input)

    pages = []

    for page_index in range(len(pdf)):
        try:
            page = pdf[page_index]
            textpage = page.get_textpage()
            text = textpage.get_text_range()
        except Exception as error:
            text = f"[ERROR: Could not extract page {page_index + 1}: {error}]"

        pages.append({
            "page_number": page_index + 1,
            "text": text
        })

    return pages


def combine_pages(pages):
    """
    Combines extracted PDF pages into a single text string
    while preserving page boundaries.
    """

    full_text = ""

    for page in pages:
        full_text += f"\n--- PAGE {page['page_number']} ---\n"
        full_text += page["text"]

    return full_text
