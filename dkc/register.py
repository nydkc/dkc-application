import re, logging
from webapp2_extras import auth, sessions
from dkc import *
from models import *

class RegisterPage(BaseHandler):

    @guest_only
    def get(self):
        self._serve_page()

    @guest_only
    def post(self):
        first_name = self.request.get('first-name')
        if first_name == '':
            self._serve_page(error="Your first name cannot be blank.")
            return
        last_name = self.request.get('last-name')
        if last_name == '':
            self._serve_page(error="Your last name cannot be blank.")
            return
        email = self.request.get('email')
        if re.search(r'^([a-zA-Z0-9+_\-\.])+@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,6})$', email) == None:
            self._serve_page(error="Please use a valid email address.")
            return
        user_name = email
        password = self.request.get('password')
        
        unique_properties = ['email']
        success, user = self.user_model.create_user(user_name, unique_properties,
            email=email, password_raw=password, first_name=first_name, last_name=last_name, pw=password)
        if not success:
            self._serve_page(error='The email, %s is already taken. Please use a different email.' % (user_name))
            return

        new_application = Application(parent=user.key)
        new_application_key = new_application.put()
        user.application = new_application_key
        user.put()
        logging.info('Created new user %s %s, with email %s', first_name, last_name, email)
        self.redirect('/login?new=1')

    def _serve_page(self, error=None):
        template_values = {
            'first_name': self.request.get('first-name'),
            'last_name': self.request.get('last-name'),
            'email': self.request.get('email'),
            'password': self.request.get('password'),
            'error': error
        }
        self.render_template('register.html', template_values)
