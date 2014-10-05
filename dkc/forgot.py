import os, webapp2, jinja2, time, logging
from webapp2_extras import auth, sessions
from google.appengine.api import mail
from dkc import *
from models import *

class ForgotPasswordHandler(BaseHandler):

    def get(self):
        self._serve_page()

    def post(self):
        username = self.request.get('email')

        user = self.user_model.get_by_auth_id(username)
        if not user:
            logging.info('Could not find any user entry for username %s', username)
            self._serve_page(not_found=True)
            return

        user_id = user.get_id()
        token = self.user_model.create_signup_token(user_id)

        verification_url = self.uri_for('verification', type='p', user_id=user_id, signup_token=token, _full=True)
        print verification_url
        
        mail.send_mail(sender="NYDKC Awards Committee <info@dkc-app.appspotmail.com>",
                       to=user.email,
                       subject="Resetting your DKC Application Password",
                       reply_to="dkc.applications@gmail.com",
                       body="""
You have requested to change the password for your DKC Application.

If you did not authorize this, then please disregard this email. Otherwise, click the link below to reset your password.

<a href="%s">%s</a>

If you have any questions or concerns, feel free to reply to this email and we will try our best to address them!

Yours in spirit and service,
The New York District Awards Committee
                       """ % (verification_url, verification_url),
                       html="""
<h2>You have requested to change the password for your DKC Application.</h2>
<p>If you did not authorize this, then please disregard this email. Otherwise, click the link below to reset your password.</p>
<p><a href="%s">%s</a></p>
<p>If you have any questions or concerns, feel free to reply to this email and we will try our best to address them!</p>
<p>Yours in spirit and service,<br>
The New York District Awards Committee</p>
                       """ % (verification_url, verification_url)
        )
        self._serve_page(email_sent=True)

    def _serve_page(self, not_found=False, email_sent=False):
        username = self.request.get('username')
        template_values = {
            'email': username,
            'not_found': not_found,
            'email_sent': email_sent
        }
        self.render_template('forgot.html', template_values)

class SetPasswordHandler(BaseHandler):

    def get(self):
        self.redirect('/forgot')

    @user_required
    def post(self):
        password = self.request.get('password')
        old_token = self.request.get('t')

        user = self.user
        user.set_password(password)
        user.put()

        self.user_model.delete_signup_token(user.get_id(), old_token)
        self.auth.unset_session()

        template_values = {
            'changed': True
        }
        self.render_template('login.html', template_values)
