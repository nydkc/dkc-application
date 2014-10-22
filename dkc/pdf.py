from StringIO import StringIO
import xhtml2pdf.pisa as pisa
 
def generate_pdf(html_data):
    #html_data = '<b>your HTML data</b>'
    html_data = html_data.encode('utf8')
    html_data = StringIO(html_data)

    output = StringIO()
    pisa.log.setLevel('WARNING') #suppress debug log output
    pdf = pisa.CreatePDF(
        html_data,
        output,
        encoding='utf-8',
    )

    pdf_data = pdf.dest.getvalue()
    return pdf_data
