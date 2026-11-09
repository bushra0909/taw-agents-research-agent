
import os
import re
import html

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    KeepInFrame
)


def generate_pdf(company_name: str, summary: str, search_results: list):

    # Vercel allows writing files inside /tmp.
    # Locally, save PDFs inside the generated folder.
    if os.getenv("VERCEL"):
        output_dir = "/tmp/generated"
    else:
        output_dir = "generated"

    os.makedirs(output_dir, exist_ok=True)

    # Make a safe filename from the company name
    filename = re.sub(
        r"[^a-zA-Z0-9]+", "_", company_name
    ).strip("_")

    file_path = os.path.join(
        output_dir,
        f"{filename}_research_brief.pdf"
    )

    # Set up the PDF page
    document = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch
    )

    # Prepare text styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=16,
        textColor=colors.HexColor("#17365D"),
        spaceAfter=10
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#17365D"),
        spaceBefore=5,
        spaceAfter=3
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=7.5,
        leading=9.5,
        spaceAfter=3
    )

    source_style = ParagraphStyle(
        "SourceText",
        parent=body_style,
        fontSize=6.5,
        leading=8
    )

    content = []

    # Add the report title
    content.append(Paragraph(
        f"{html.escape(company_name)} - Company Research Brief",
        title_style
    ))

    content.append(Paragraph(
        "Prepared using web research and AI-assisted analysis",
        body_style
    ))

    content.append(Spacer(1, 6))

    # Convert the AI summary into PDF paragraphs
    for line in summary.splitlines():

        line = line.strip()

        if not line or line.lower() == "sources:":
            continue

        if line.startswith("**") and line.endswith("**"):
            heading = line.strip("*")
            content.append(Paragraph(
                html.escape(heading),
                heading_style
            ))

        elif line.startswith("* ") or line.startswith("- "):
            bullet = line[2:]
            content.append(Paragraph(
                "&#8226; " + html.escape(bullet),
                body_style
            ))

        elif line.startswith("Sources:"):
            break

        else:
            content.append(Paragraph(
                html.escape(line.replace("**", "")),
                body_style
            ))

    # Add clickable source links
    content.append(Spacer(1, 5))
    content.append(Paragraph("Research Sources", heading_style))

    for result in search_results:
        title = html.escape(result.get("title", "Source"))
        url = result.get("url", "")

        if url.startswith(("https://", "http://")):
            safe_url = html.escape(url, quote=True)

            content.append(Paragraph(
                f'<link href="{safe_url}" color="blue">{title}</link>',
                source_style
            ))

    # Fit everything onto one page
    page_content = KeepInFrame(
        document.width,
        document.height,
        content,
        mode="shrink"
    )

    document.build([page_content])

    return file_path
