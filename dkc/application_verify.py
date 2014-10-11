import os, webapp2, jinja2, logging
from google.appengine.ext import ndb
from dkc import *
from models import *

class ApplicationVerificationHandler(BaseHandler):

    def post(self):
        user_id = self.request.get('user-id')
        signup_token = self.request.get('token')

        user, ts = self.user_model.get_by_auth_token(int(user_id), signup_token, 'signup')

        if not user:
            logging.info('Unauthorized verification by id "%s"', user_id)
            self.abort(401)
            return

        application = user.application.get()
        if application.verification_ltg_token == signup_token:
            application.verification_ltg = True
        elif application.verification_club_president_token == signup_token:
            application.verification_club_president = True
        elif application.verification_faculty_advisor_token == signup_token:
            application.verification_faculty_advisor = True
        else:
            self.render_template('verification-error.html')
            return

        application.put()

        template_values = {
            'applicant': user,
        }
        self.render_template('verification-success.html', template_values)

        self.user_model.delete_signup_token(user.get_id(), signup_token)
