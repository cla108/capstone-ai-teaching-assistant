import pypdfium2 as pdfium


def extract_text_from_pdf(pdf_file):
    """
    Extracts raw text from each page of a PDF document.

    Parameters:
        pdf_file (UploadedFile | str):
            PDF file uploaded through Streamlit or local file path.

    Returns:
        list[dict]:
            List of page dictionaries containing:
            - page_number (int)
            - text (str)

    Purpose:
        Converts textbook PDFs into structured page-level text
        for downstream processing such as TOC parsing,
        chapter extraction, semantic chunking, and RAG retrieval.
    """

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
    """
    Combines extracted PDF pages into a single text string
    while preserving page boundaries.

    Parameters:
        pages (list[dict]):
            Output from extract_text_from_pdf().

    Returns:
        str:
            Full textbook text with page markers.

    Example Output:
        --- PAGE 1 ---
        textbook text...

        --- PAGE 2 ---
        textbook text...

    Purpose:
        Preserves page references required for:
        - Table of contents reconstruction
        - chapter boundary detection
        - section extraction
        - citation tracing
        - hallucination verification
    """

    full_text = ""

    for page in pages:
        full_text += f"\n--- PAGE {page['page_number']} ---\n"
        full_text += page["text"]

    return full_text
