import os
from io import BytesIO

import fitz  # PyMuPDF


def extract_images_from_pdf(
    pdf_file,
    start_page,
    end_page,
    chapter_number,
    output_dir="outputs/images"
):
    """
    Extracts embedded images from a chapter page range.

    Pages are expected to use the same page numbering system
    already used by the extracted PDF pages.
    """

    if hasattr(pdf_file, "getvalue"):
        pdf_bytes = pdf_file.getvalue()
        pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
    else:
        pdf = fitz.open(pdf_file)

    chapter_dir = os.path.join(output_dir, f"chapter_{chapter_number}")
    os.makedirs(chapter_dir, exist_ok=True)

    extracted_images = []

    for page_number in range(start_page, end_page + 1):
        page_index = page_number - 1

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
                    f"page_{page_number}_"
                    f"image_{image_index}.{image_ext}"
                )

                image_path = os.path.join(chapter_dir, image_filename)

                with open(image_path, "wb") as image_file:
                    image_file.write(image_bytes)

                extracted_images.append({
                    "chapter_number": chapter_number,
                    "page_number": page_number,
                    "image_index": image_index,
                    "image_path": image_path,
                    "image_filename": image_filename,
                    "type": "image"
                })

            except Exception as error:
                extracted_images.append({
                    "chapter_number": chapter_number,
                    "page_number": page_number,
                    "image_index": image_index,
                    "error": str(error),
                    "type": "image_error"
                })

    return extracted_images
