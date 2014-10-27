import os, webapp2, jinja2
from dkc import *
from application import *
from application_verify import ApplicationVerificationHandler
from register import RegisterPage
from login import LoginPage
from logout import LogoutPage
from forgot import ForgotPasswordHandler, SetPasswordHandler
from verify import VerificationHandler
from upload import *
from download import *
from test import TestHandler

class MainPage(BaseHandler):

    def get(self):
        if 'dkc-app.nydkc.org' in os.environ['HTTP_HOST']:
            template = JINJA_ENVIRONMENT.get_template('coming_soon.html')
            self.response.write(template.render({}))
        else:
            self.render_template('index.html')

application = webapp2.WSGIApplication([
    ('/application/personal-statement', ApplicationPersonalStatement),
    ('/application/projects', ApplicationProjects),
    ('/application/involvement', ApplicationInvolvement),
    ('/application/activities', ApplicationActivities),
    ('/application/activities/upload', ApplicationActivitiesUploadHandler),
    ('/application/scoring', ApplicationScoring),
    ('/application/verification', ApplicationVerification),
    ('/verification_success', ApplicationVerificationHandler),
    ('/application/profile', ApplicationProfile),
    ('/application/upload', ApplicationUploadHandler),
    ('/application/submit', ApplicationSubmit),
    ('/application/download/pdf/([^/]+)?', PDFGeneration),
    #('/application/download/docx/([^/]+)?', DOCXGeneration),
    ('/application.*', ApplicationOverview),
    ('/login', LoginPage),
    ('/logout', LogoutPage),
    ('/register', RegisterPage),
    ('/forgot', ForgotPasswordHandler),
    ('/reset_password', SetPasswordHandler),
    webapp2.Route('/<type:p|v>/<user_id:\d+>-<signup_token:.+>', handler=VerificationHandler, name='verification'),
    ('/serve/([^/]+)/?.*', ServeHandler),
    ('/delete/([^/]+)?', DeleteHandler),
    ('/test/([^/]+)?', TestHandler),
    ('/.*', MainPage)
], debug=True, config=config)
