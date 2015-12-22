import logging
from webapp2_extras import auth, sessions
from webapp2_extras.auth import InvalidAuthIdError, InvalidPasswordError
from dkc import *
from models import *

class LoginPage(BaseHandler):

    @guest_only
    def get(self):
        if self.request.get('new') != '':
            self._serve_page(new_account=True)
        else:
            self._serve_page()

    @guest_only
    def post(self):
        username = self.request.get('email')
        password = self.request.get('password')
        try:
            user = self.auth.get_user_by_password(username, password, remember=True)
            self.redirect('/application')
        except (InvalidAuthIdError, InvalidPasswordError) as e:
            logging.info('Login failed for user %s because of %s', username, type(e))
            self._serve_page(failed=True)

    def _serve_page(self, failed=False, new_account=False):
        username = self.request.get('email')
        template_values = {
            'email': username,
            'failed': failed,
            'new_account': new_account
        }
        self.render_template('login.html', template_values)
