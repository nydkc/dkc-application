import os, webapp2, jinja2
from dkc import *
from application import *
from register import RegisterPage
from login import LoginPage
from logout import LogoutPage
from forgot import ForgotPasswordHandler, VerificationHandler, SetPasswordHandler
from test import TestHandler

class MainPage(BaseHandler):

    def get(self):
        if 'dkc-app.nydkc.org' in os.environ['HTTP_HOST']:
            self.render_template('coming_soon.html')
        else:
            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render({}))

application = webapp2.WSGIApplication([
    ('/application/personal-statement', ApplicationPersonalStatement),
    ('/application/projects', ApplicationProjects),
    ('/application/involvement', ApplicationInvolvement),
    ('/application/activities', ApplicationActivities),
    ('/application/scoring', ApplicationScoring),
    ('/application/verification', ApplicationVerification),
    ('/application/profile', ApplicationProfile),
    ('/application/.*', ApplicationOverview),
    ('/login', LoginPage),
    ('/logout', LogoutPage),
    ('/register', RegisterPage),
    ('/forgot', ForgotPasswordHandler),
    webapp2.Route('/<type:p>/<user_id:\d+>-<signup_token:.+>', handler=VerificationHandler, name='verification'),
    ('/reset_password', SetPasswordHandler),
    ('/test/.*', TestHandler),
    ('/.*', MainPage)
], debug=True, config=config)
