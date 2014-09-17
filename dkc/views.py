import os, webapp2, jinja2
from dkc import *
from application import *
from register import RegisterPage
from login import LoginPage
from logout import LogoutPage
from forgot import ForgotPasswordHandler, VerificationHandler, SetPasswordHandler

class MainPage(BaseHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render({}))

application = webapp2.WSGIApplication([
    ('/application/personal-statement', ApplicationPersonalStatement),
#    ('/application/projects', ApplicationProjects),
#    ('/application/involvement', ApplicationInvolvement),
#    ('/application/activities', ApplicationActivities),
#    ('/application/scoring', ApplicationScoring),
#    ('/application/verification', ApplicationVerification),
    ('/application.*', ApplicationProfile),
    ('/login', LoginPage),
    ('/logout', LogoutPage),
    ('/register', RegisterPage),
    ('/forgot', ForgotPasswordHandler),
    webapp2.Route('/<type:p>/<user_id:\d+>-<signup_token:.+>', handler=VerificationHandler, name='verification'),
    ('/reset_password', SetPasswordHandler),
    ('/.*', MainPage)
], debug=True, config=config)
