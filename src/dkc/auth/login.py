# import logging
# from webapp2_extras import auth, sessions
# from webapp2_extras.auth import InvalidAuthIdError, InvalidPasswordError
# from dkc import *
# from models import *

# class LoginPage(BaseHandler):

#     @guest_only
#     def get(self):
#         if self.request.get('new') != '':
#             self._serve_page(new_account=True)
#         else:
#             self._serve_page()

#     @guest_only
#     def post(self):
#         failures_cookie = self.request.cookies.get('failures')
#         try:
#             failures = int(failures_cookie) + 1
#         except:
#             failures = 1
#         self.response.set_cookie('failures', str(failures), max_age=3600)
#         if failures > 5:
#             config = ndb.Key(Settings, 'config').get()
#             grecaptcha = self.request.get('g-recaptcha-response')
#             recaptcha_success = util.verify_captcha(config.recaptcha_secret, grecaptcha)
#             if not recaptcha_success:
#                 self._serve_page(failed=True)
#                 return

#         username = self.request.get('email')
#         password = self.request.get('password')
#         try:
#             user = self.auth.get_user_by_password(username, password, remember=True)
#             self.response.delete_cookie('failures')
#             self.redirect('/application')
#         except (InvalidAuthIdError, InvalidPasswordError) as e:
#             logging.info('Login failed for user %s because of %s', username, type(e))
#             self._serve_page(failed=True)

#     def _serve_page(self, failed=False, new_account=False):
#         failures_cookie = self.request.cookies.get('failures')
#         try:
#             failures = int(failures_cookie)
#         except:
#             failures = 0

#         config = ndb.Key(Settings, 'config').get()
#         recaptcha_site_key = config.recaptcha_site_key

#         username = self.request.get('email')
#         template_values = {
#             'email': username,
#             'failed': failed,
#             'failures': failures,
#             'new_account': new_account,
#             'recaptcha_site_key': recaptcha_site_key
#         }
#         self.render_template('login.html', template_values)

from flask import request, render_template
from flask_login import login_user
from . import auth_bp
from . import models


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.args.get("email")
        user = models.User.query(models.User.email == email).get()
        login_user(user)

    # TODO(dannyqiu): dynamically get values
    email = "danny"
    failed = True
    failures = 1
    new_account = True
    recaptcha_site_key = "abcdef"
    template_values = {
        "email": email,
        "failed": failed,
        "failures": failures,
        "new_account": new_account,
        "recaptcha_site_key": recaptcha_site_key,
    }
    return render_template("auth/login.html", **template_values)
