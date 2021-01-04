import logging
from google.appengine.api import users
from dkc import *
from models import User

class PDFGeneration(BaseHandler):

    def get(self, user_id,):
        token = self.request.get("t")
        token_id = self.request.get("a")
        if token and token_id: # Used for verification bypass
            user, ts = self.user_model.get_by_auth_token(int(token_id), token, 'signup')
            if not user:
                logging.info('Could not verify token to view application with id "%s" and signup token "%s"', token_id, token)
                self.display_message("Invalid URL to view application!")
                return
        elif users.get_current_user(): # Logged in to Google and connected with dkc-application
            if not users.is_current_user_admin():
                logging.info('Non-admin access of aplication %s by %s', user_id, users.get_current_user().email())
                self.response.set_status(401);
                self.display_message("You are not an admin! Only admins are allowed to view applications.")
                return
        else:
            if self.user is None: # Prevent access from users not logged in
                logging.info("Unauthorized access of application %s", user_id)
                self.response.set_status(401);
                self.display_message("You are not authorized to view this application!")
                return
            elif user_id != str(self.user_info['user_id']): # Prevent access from other users
                applicant = self.user
                logging.info("Attempted access of application %s by %s" % (user_id, applicant.email))
                self.response.set_status(401);
                self.display_message("%s %s, please do not attempt to access the applications of other applicants." % (applicant.first_name, applicant.last_name))
                return

        config = ndb.Key(Settings, 'config').get()
        applicant = User.get_by_id(int(user_id))
        application = applicant.application.get()
        template_values = {
            'config': config,
            'applicant': applicant,
            'application': application,
            'STATIC_DIR': os.path.normpath(os.path.join(os.path.dirname(__file__), '../static'))
        }
        template = JINJA_ENVIRONMENT.get_template('pdf/application-pdf.html')
        html = template.render(template_values)
        #self.response.write(html)
        self.response.headers['content-type'] = 'application/pdf'
        self.response.write(generate_pdf(html))
