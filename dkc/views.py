import webapp2
from google.appengine.ext import ndb
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
from survey import SurveyHandler
from test import TestHandler

class MainPage(BaseHandler):

    def get(self):
        config = ndb.Key(Settings, 'config').get()
        template_values = {
            'config': config
        }
        self.render_template('index.html', template_values)

application = webapp2.WSGIApplication([
    ('/application/personal-statement', ApplicationPersonalStatement),
    ('/application/projects', ApplicationProjects),
    ('/application/involvement', ApplicationInvolvement),
    ('/application/activities', ApplicationActivities),
    ('/application/activities/upload', ApplicationActivitiesUploadHandler),
    ('/application/other', ApplicationOther),
    ('/application/verification', ApplicationVerification),
    ('/verification_success', ApplicationVerificationHandler),
    ('/application/profile', ApplicationProfile),
    ('/application/upload', ApplicationUploadHandler),
    ('/application/submit', ApplicationSubmit),
    ('/application/download/pdf/(\d+)-.*.pdf', PDFGeneration),
    ('/application.*', ApplicationOverview),
    ('/login', LoginPage),
    ('/logout', LogoutPage),
    ('/register', RegisterPage),
    ('/forgot', ForgotPasswordHandler),
    ('/reset_password', SetPasswordHandler),
    webapp2.Route('/<type:p|v>/<user_id:\d+>-<signup_token:.+>', handler=VerificationHandler, name='verification'),
    ('/serve/([^/]+)/?.*', ServeHandler),
    ('/delete/([^/]+)?', DeleteHandler),
    ('/survey.*', SurveyHandler),
    ('/test/([^/]+)?', TestHandler),
    ('/.*', MainPage)
], debug=True, config=config)
