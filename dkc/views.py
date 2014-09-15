import os, webapp2, jinja2
from dkc import *
from application import ApplicationPage
from register import RegisterPage
from login import LoginPage
from logout import LogoutPage
from forgot import ForgotPasswordHandler, VerificationHandler, SetPasswordHandler

class MainPage(BaseHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render({}))

application = webapp2.WSGIApplication([
    ('/application', ApplicationPage),
    ('/login', LoginPage),
    ('/logout', LogoutPage),
    ('/register', RegisterPage),
    ('/forgot', ForgotPasswordHandler),
    webapp2.Route('/<type:p>/<user_id:\d+>-<signup_token:.+>', handler=VerificationHandler, name='verification'),
    ('/reset_password', SetPasswordHandler),
    ('/.*', MainPage)
], debug=True, config=config)
