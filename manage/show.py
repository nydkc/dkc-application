import urllib
from manage import *
from models import *
import query

class ShowHandler(AdminBaseHandler):

    def get(self, email):
        config = ndb.Key(Settings, 'config').get()
        if not config:
            config = Settings(id='config')
        due_date = config.due_date

        email = str(urllib.unquote(email))
        applicant, application = query.get_application_by_email(email)

        template_values = {
            'applicant': applicant,
            'application': application,
            'applicant_id': applicant.get_id(),
            'admin_url': '/admin/show/' + email,
            'DUE_DATE': due_date
        }
        self.render_template('admin-show.html', template_values)

    def post(self, email):
        email = str(urllib.unquote(email))
        applicant, application = query.get_application_by_email(email)

        if self.request.get('notes'):
            application.notes = self.request.get('notes')
        elif self.request.get('graded'):
            application.graded = not application.graded
        application.put()
