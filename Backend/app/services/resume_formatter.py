from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.models import ResumeData
import os
import uuid

def generate_pdf(parsed_data: ResumeData) -> str:
    output_dir = "app/static/pdfs"
    os.makedirs(output_dir, exist_ok=True)

    pdf_filename = f"{uuid.uuid4()}.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)

    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 10)

    margin = 72  # 1 inch margin
    usable_width = width - 2 * margin
    y_position = height - margin
    line_height = 13

    def write_wrapped_line(text, indent=0):
        nonlocal y_position
        x_start = margin + indent
        words = text.split()
        line = ""
        for word in words:
            if c.stringWidth(line + word + " ", "Helvetica", 10) < (usable_width - indent):
                line += word + " "
            else:
                if y_position < margin:
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y_position = height - margin
                c.drawString(x_start, y_position, line)
                y_position -= line_height
                line = word + " "
        if line:
            if y_position < margin:
                c.showPage()
                c.setFont("Helvetica", 10)
                y_position = height - margin
            c.drawString(x_start, y_position, line)
            y_position -= line_height

    # Basic Info
    write_wrapped_line(f"Name: {parsed_data.name}")
    write_wrapped_line(f"Email: {parsed_data.email}")
    write_wrapped_line(f"Phone: {parsed_data.phone}")
    write_wrapped_line(f"Skills: {', '.join(parsed_data.skills)}")
    y_position -= line_height

    # Experience
    write_wrapped_line("Experience:")
    for job in parsed_data.experience:
        write_wrapped_line(f"{job['company']} ({job['position']})", indent=20)
        for responsibility in job['responsibilities']:
            write_wrapped_line(f"- {responsibility}", indent=40)
    y_position -= line_height

    # Projects
    write_wrapped_line("Projects:")
    for project in parsed_data.projects:
        write_wrapped_line(f"Project: {project['name']} ({project['date']})", indent=20)
        write_wrapped_line(f"Technologies: {', '.join(project['technologies'])}", indent=40)
        write_wrapped_line(f"Description: {project['description']}", indent=40)
        y_position -= line_height

    # Certifications
    write_wrapped_line("Certifications:")
    for cert in parsed_data.certifications:
        write_wrapped_line(f"- {cert}", indent=20)
    y_position -= line_height

    # Achievements
    write_wrapped_line("Achievements:")
    for achievement in parsed_data.achievements:
        write_wrapped_line(f"- {achievement}", indent=20)

    c.save()
    return pdf_path
