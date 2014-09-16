import os, webapp2, jinja2
from google.appengine.ext import ndb
from dkc import *
from models import *

class ApplicationPage(BaseHandler):

    @user_required
    def get(self):
        applicant = self.user
        application_key = applicant.application
        application = application_key.get()
        template_values = {
            'applicant': applicant,
            'application': application,
            'form_key': application_key.urlsafe()
        }
        self.render_template('application.html', template_values)

    def post(self):
        application_key = ndb.Key(urlsafe=self.request.get('form-key'))
        application = application_key.get()
        applicant = application_key.parent().get()

        application.personal_statement = self.request.get('personal-statement')
        application.put()

        template_values = {
            'applicant': applicant,
            'application': application,
            'form_key': application_key.urlsafe()
        }
        #self.render_template('application.html', template_values)
        self.response.write(self.request.arguments());
