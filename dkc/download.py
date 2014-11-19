import logging
from dkc import *
from dkc.models import User
from google.appengine.api import users
from StringIO import StringIO
import xhtml2pdf.pisa as pisa

class PDFGeneration(BaseHandler):

    def get(self, user_id):
        if users.get_current_user():
            if not users.is_current_user_admin():
                self.abort(401)
                return
        else:
            if self.user == None: # Prevent access from users no logged in
                logging.info("Unauthorized access of application %s", user_id)
                self.abort(401)
                return
            elif user_id != str(self.user_info['user_id']): # Prevent access from other users
                logging.info("Attempted access of application %s by %s", user_id, self.user.email)
                self.abort(401)
                return

        applicant = User.get_by_id(int(user_id))
        application = applicant.application.get()
        template_values = {
            'applicant': applicant,
            'application': application,
            'STATIC_DIR': os.path.join(os.path.dirname(__file__), '../static')
        }
        template = JINJA_ENVIRONMENT.get_template('pdf/application-pdf.html')
        html = template.render(template_values)
        #self.response.write(html)
        self.response.headers['content-type'] = 'application/pdf'
        self.response.write(generate_pdf(html))
 
def generate_pdf(html_data):
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
