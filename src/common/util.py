import io
import xhtml2pdf.pisa as pisa

def generate_pdf(html_data: str):
    output = io.BytesIO()
    pisa.log.setLevel("WARNING")  # suppress debug log output
    pdf = pisa.CreatePDF(
        html_data,
        dest=output,
        encoding="utf-8",
    )
    pdf_data = pdf.dest.getvalue()
    return pdf_data
