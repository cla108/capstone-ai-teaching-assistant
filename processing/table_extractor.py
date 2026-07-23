import os

import fitz  # PyMuPDF


def get_large_rectangles(page, min_width_ratio=0.20, min_height=25):
    """
    Detects large rectangular boxed regions on a PDF page.
    """

    rectangles = []

    for drawing in page.get_drawings():
        for item in drawing["items"]:
            if item[0] == "re":
                rect = item[1]

                if (
                    rect.width >= page.rect.width * min_width_ratio
                    and rect.height >= min_height
                ):
                    rectangles.append(rect)

    return rectangles


def get_line_based_boxes(page, min_width_ratio=0.20, min_height=25):
    """
    Detects boxed regions made from individual line segments.
    """

    horizontal_lines = []
    vertical_lines = []

    for drawing in page.get_drawings():
        for item in drawing["items"]:
            if item[0] != "l":
                continue

            p1 = item[1]
            p2 = item[2]

            if abs(p1.y - p2.y) < 2:
                horizontal_lines.append((p1, p2))

            elif abs(p1.x - p2.x) < 2:
                vertical_lines.append((p1, p2))

    candidate_boxes = []

    for h1_start, h1_end in horizontal_lines:
        for h2_start, h2_end in horizontal_lines:
            if h2_start.y <= h1_start.y:
                continue

            top_y = h1_start.y
            bottom_y = h2_start.y

            left_x = min(h1_start.x, h1_end.x, h2_start.x, h2_end.x)
            right_x = max(h1_start.x, h1_end.x, h2_start.x, h2_end.x)

            rect = fitz.Rect(left_x, top_y, right_x, bottom_y)

            if (
                rect.width >= page.rect.width * min_width_ratio
                and rect.height >= min_height
            ):
                candidate_boxes.append(rect)

    return candidate_boxes


def remove_nested_rectangles(rectangles):
    """
    Removes rectangles inside larger rectangles.
    """

    outer_rectangles = []

    for rect in rectangles:
        is_inside_another = False

        for other in rectangles:
            if rect == other:
                continue

            if other.contains(rect):
                is_inside_another = True
                break

        if not is_inside_another:
            outer_rectangles.append(rect)

    return outer_rectangles


def merge_overlapping_rectangles(rectangles):
    """
    Merges overlapping or very close rectangles.
    """

    merged = []

    for rect in sorted(rectangles, key=lambda r: (r.y0, r.x0)):
        was_merged = False

        for i, existing in enumerate(merged):
            if existing.intersects(rect):
                merged[i] = existing | rect
                was_merged = True
                break

        if not was_merged:
            merged.append(rect)

    return merged


def extract_boxed_objects_as_images(
    pdf_file,
    start_page,
    end_page,
    chapter_number,
    page_offset=0,
    output_dir="outputs/boxed_objects"
):
    """
    Extracts boxed visual objects from a chapter:
    tables, figures, diagrams, and boxed layouts.
    """

    if hasattr(pdf_file, "getvalue"):
        pdf_bytes = pdf_file.getvalue()
        pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
    else:
        pdf = fitz.open(pdf_file)

    chapter_dir = os.path.join(output_dir, f"chapter_{chapter_number}")
    os.makedirs(chapter_dir, exist_ok=True)

    extracted_objects = []

    for textbook_page_number in range(start_page, end_page + 1):
        pdf_page_number = textbook_page_number + page_offset
        page_index = pdf_page_number - 1

        if page_index < 0 or page_index >= len(pdf):
            continue

        page = pdf[page_index]

        rectangles = []
        rectangles.extend(get_large_rectangles(page))
        rectangles.extend(get_line_based_boxes(page))

        rectangles = remove_nested_rectangles(rectangles)
        rectangles = merge_overlapping_rectangles(rectangles)

        for object_index, rect in enumerate(rectangles, start=1):
            crop_rect = fitz.Rect(
                max(rect.x0 - 10, 0),
                max(rect.y0 - 30, 0),
                min(rect.x1 + 10, page.rect.width),
                min(rect.y1 + 30, page.rect.height)
            )

            pix = page.get_pixmap(
                matrix=fitz.Matrix(2, 2),
                clip=crop_rect
            )

            filename = (
                f"chapter_{chapter_number}_"
                f"textbook_page_{textbook_page_number}_"
                f"pdf_page_{pdf_page_number}_"
                f"boxed_object_{object_index}.png"
            )

            path = os.path.join(chapter_dir, filename)
            pix.save(path)

            extracted_objects.append({
                "type": "boxed_object",
                "chapter_number": chapter_number,
                "textbook_page_number": textbook_page_number,
                "pdf_page_number": pdf_page_number,
                "object_index": object_index,
                "filename": filename,
                "path": path,
                "bbox": [
                    crop_rect.x0,
                    crop_rect.y0,
                    crop_rect.x1,
                    crop_rect.y1
                ]
            })

    pdf.close()

    return extracted_objects





def extract_chapter_text(pages, chapter):
    """
    Extract full chapter text from PDF pages.
    """

    selected_pages = []

    pdf_start = chapter["pdf_start_page"]
    pdf_end = chapter["pdf_end_page"]

    for page in pages:
        page_number = page["page_number"]

        if pdf_end is None:
            is_inside_chapter = page_number >= pdf_start
        else:
            is_inside_chapter = (
                page_number >= pdf_start
                and page_number <= pdf_end
            )

        if is_inside_chapter:
            selected_pages.append(page["text"])

    chapter_copy = chapter.copy()
    chapter_copy["text"] = "\n".join(selected_pages)

    return chapter_copy
def extract_all_chapters_text(pages, chapters):
    """
    Extract text for all chapters.

    Parameters
    ----------
    pages : list
        PDF pages extracted from the textbook.

    chapters : list
        Chapter metadata with PDF page ranges.

    Returns
    -------
    list
        Chapters including extracted text.
    """

    return [
        extract_chapter_text(pages, chapter)
        for chapter in chapters
    ]
