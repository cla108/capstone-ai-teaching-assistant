from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch


def generate_lesson_pdf(
    instructor_guide,
    output_path
):
    """
    Generates a PDF containing only the instructor guide.
    """

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
            story.append(
                Paragraph(
                    line.replace("# ", ""),
                    styles["Title"]
                )
            )

        elif line.startswith("## "):
            story.append(
                Paragraph(
                    line.replace("## ", ""),
                    styles["Heading2"]
                )
            )

        else:
            story.append(
                Paragraph(
                    line,
                    styles["BodyText"]
                )
            )

    doc.build(story)

    return output_path
