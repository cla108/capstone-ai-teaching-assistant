import os

import fitz  # PyMuPDF


def extract_images_from_pdf(
    pdf_file,
    start_page,
    end_page,
    chapter_number,
    page_offset=0,
    output_dir="outputs/images"
):
    """
    Extracts embedded images from a chapter page range.

    start_page and end_page are textbook page numbers.
    page_offset converts textbook page numbers into PDF page numbers.
    """

    if hasattr(pdf_file, "getvalue"):
        pdf_bytes = pdf_file.getvalue()
        pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
    else:
        pdf = fitz.open(pdf_file)

    chapter_dir = os.path.join(output_dir, f"chapter_{chapter_number}")
    os.makedirs(chapter_dir, exist_ok=True)

    extracted_images = []

    for textbook_page_number in range(start_page, end_page + 1):
        pdf_page_number = textbook_page_number + page_offset
        page_index = pdf_page_number - 1

        if page_index < 0 or page_index >= len(pdf):
            continue

        page = pdf[page_index]
        images = page.get_images(full=True)

        for image_index, image in enumerate(images, start=1):
            xref = image[0]

            try:
                base_image = pdf.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                image_filename = (
                    f"chapter_{chapter_number}_"
                    f"textbook_page_{textbook_page_number}_"
                    f"pdf_page_{pdf_page_number}_"
                    f"image_{image_index}.{image_ext}"
                )

                image_path = os.path.join(chapter_dir, image_filename)

                with open(image_path, "wb") as image_file:
                    image_file.write(image_bytes)

                extracted_images.append({
                    "type": "image",
                    "chapter_number": chapter_number,
                    "textbook_page_number": textbook_page_number,
                    "pdf_page_number": pdf_page_number,
                    "image_index": image_index,
                    "image_filename": image_filename,
                    "image_path": image_path
                })

            except Exception as error:
                extracted_images.append({
                    "type": "image_error",
                    "chapter_number": chapter_number,
                    "textbook_page_number": textbook_page_number,
                    "pdf_page_number": pdf_page_number,
                    "image_index": image_index,
                    "error": str(error)
                })

    pdf.close()

    return extracted_images
