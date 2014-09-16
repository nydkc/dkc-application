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
            'application': application
        }
        self.render_template('application.html', template_values)
