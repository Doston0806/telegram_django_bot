from django.template.loader import render_to_string
from weasyprint import HTML
from io import BytesIO

def generate_pdf(template_name, context):
    html_string = render_to_string(template_name, context)
    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(pdf_file)
    pdf_file.seek(0)
    return pdf_file


