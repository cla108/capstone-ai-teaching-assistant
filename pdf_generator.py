import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch


def generate_lesson_pdf(
    instructor_guide,
    images,
    boxed_objects,
    output_path
):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    story = []

    for line in instructor_guide.split("\n"):
        line = line.strip()

        if not line:
            story.append(Spacer(1, 0.15 * inch))
            continue

        if line.startswith("# "):
            story.append(Paragraph(line.replace("# ", ""), styles["Title"]))

        elif line.startswith("## "):
            story.append(Paragraph(line.replace("## ", ""), styles["Heading2"]))

        else:
            story.append(Paragraph(line, styles["BodyText"]))

    story.append(PageBreak())
    story.append(Paragraph("Figures, Images, and Tables", styles["Title"]))

    all_visuals = []

    for image in images:
        if image["type"] == "image":
            all_visuals.append({
                "path": image["image_path"],
                "label": f"Image - Textbook Page {image['textbook_page_number']}"
            })

    for obj in boxed_objects:
        all_visuals.append({
            "path": obj["path"],
            "label": f"Boxed Object - Textbook Page {obj['textbook_page_number']}"
        })

    if not all_visuals:
        story.append(Paragraph("No visual elements extracted for this chapter.", styles["BodyText"]))

    for visual in all_visuals:
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(visual["label"], styles["Heading3"]))

        try:
            img = Image(visual["path"])
            img._restrictSize(6.5 * inch, 7.5 * inch)
            story.append(img)
        except Exception:
            story.append(Paragraph(f"Could not load image: {visual['path']}", styles["BodyText"]))

    doc.build(story)

    return output_path
