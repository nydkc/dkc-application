from dkc import *
from dkc.models import User
from google.appengine.api import users
from StringIO import StringIO
import xhtml2pdf.pisa as pisa

class PDFGeneration(BaseHandler):

    def get(self, user_id):
        if users.get_current_user() or user_id == str(self.user.get_id()):
            applicant = User.get_by_id(int(user_id))
            application = applicant.application.get()
            template_values = {
                'applicant': applicant,
                'application': application,
                'STATIC_DIR': 'static'
            }
            template = JINJA_ENVIRONMENT.get_template('application-pdf.html')
            html = template.render(template_values)
            #self.response.write(html)
            self.response.headers['content-type'] = 'application/pdf'
            self.response.write(generate_pdf(html))
        else:
            self.abort(401)
 
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
