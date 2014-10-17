import os, webapp2, jinja2, time, logging
from webapp2_extras import auth, sessions
from google.appengine.api import mail
from dkc import *
from models import *

class VerificationHandler(BaseHandler):

    def get(self, *args, **kwargs):
        user = None
        user_id = kwargs['user_id']
        signup_token = kwargs['signup_token']
        verification_type = kwargs['type']

        user, ts = self.user_model.get_by_auth_token(int(user_id), signup_token, 'signup')

        if not user:
            logging.info('Could not find any user with id "%s" and signup token "%s"', user_id, signup_token)
            self.display_message("Invalid Verification Link!")
            return

        if verification_type == 'p':
            self.auth.set_session(self.auth.store.user_to_dict(user), remember=True)
            template_values = {
                'token': signup_token
            }
            self.render_template('reset_password.html', template_values)
        elif verification_type == 'v':
            application = user.application.get()
            template_values = {
                'applicant': user,
                'application': application,
                'user_id': user_id,
                'token': signup_token
            }
            if application.verification_ltg_token == signup_token:
                self.render_template('verification-ltg.html', template_values)
            elif application.verification_club_president_token == signup_token:
                self.render_template('verification-club-president.html', template_values)
            elif application.verification_faculty_advisor_token == signup_token:
                self.render_template('verification-faculty-advisor.html', template_values)
            else:
                self.render_template('verification-error.html')
        else:
            self.display_message("Invalid Verification Link!")
