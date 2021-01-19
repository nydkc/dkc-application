# import webapp2
# from google.cloud import ndb
# from dkc import BaseHandler, WEBAPP2_CONFIG
# from application import *
# from application_verify import ApplicationVerificationHandler
# from register import RegisterPage
# from login import LoginPage
# from logout import LogoutPage
# from forgot import ForgotPasswordHandler, SetPasswordHandler
# from verify import VerificationHandler
# from upload import ApplicationActivitiesUploadHandler, ApplicationUploadHandler, ServeHandler, DeleteHandler
# from download import PDFGeneration
# from survey import SurveyHandler
# from test import TestHandler
# from manage.models import Settings

# application = webapp2.WSGIApplication([
#     ('/application/personal-statement', ApplicationPersonalStatement),
#     ('/application/projects', ApplicationProjects),
#     ('/application/involvement', ApplicationInvolvement),
#     ('/application/activities', ApplicationActivities),
#     ('/application/activities/upload', ApplicationActivitiesUploadHandler),
#     ('/application/other', ApplicationOther),
#     ('/application/verification', ApplicationVerification),
#     ('/verification_success', ApplicationVerificationHandler),
#     ('/application/profile', ApplicationProfile),
#     ('/application/upload', ApplicationUploadHandler),
#     ('/application/submit', ApplicationSubmit),
#     ('/application/download/pdf/(\d+)-.*.pdf', PDFGeneration),
#     ('/application.*', ApplicationOverview),
#     ('/login', LoginPage),
#     ('/logout', LogoutPage),
#     ('/register', RegisterPage),
#     ('/forgot', ForgotPasswordHandler),
#     ('/reset_password', SetPasswordHandler),
#     webapp2.Route('/<type:p|v>/<user_id:\d+>-<signup_token:.+>', handler=VerificationHandler, name='verification'),
#     ('/serve/([^/]+)/.*', ServeHandler),
#     ('/delete/([^/]+)', DeleteHandler),
#     ('/survey.*', SurveyHandler),
#     ('/test/([^/]+)?', TestHandler),
#     ('/.*', MainPage)
# ], debug=True, config=WEBAPP2_CONFIG)


from dkc.index import index_bp
from dkc.webhooks import webhooks_bp
from dkc.auth.views import auth_bp
from dkc.application.views import application_bp
from dkc.dummy.views import dummy_bp
from dkc.verify.views import verify_bp


def register_blueprints_to(app):
    app.register_blueprint(index_bp)
    app.register_blueprint(webhooks_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(application_bp, url_prefix='/application')
    app.register_blueprint(dummy_bp, url_prefix="/dummy")
    app.register_blueprint(verify_bp, url_prefix="/verify")
