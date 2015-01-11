import urllib
from manage import *
import query

class ShowHandler(AdminBaseHandler):

    def get(self, email):
        email = str(urllib.unquote(email))
        applicant, application = query.get_application_by_email(email)

        template_values = {
            'applicant': applicant,
            'application': application,
            'applicant_id': applicant.get_id(),
            'admin_url': '/admin/show/' + email
        }
        self.render_template('admin-show.html', template_values)

    def post(self, email):
        email = str(urllib.unquote(email))
        applicant, application = query.get_application_by_email(email)

        application.notes = self.request.get('notes')
        application.put()
