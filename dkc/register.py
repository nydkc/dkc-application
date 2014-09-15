import os, webapp2, jinja2
from webapp2_extras import auth, sessions
from dkc import *
from models import *

class RegisterPage(BaseHandler):

    @guest_only
    def get(self):
        self.render_template('register.html')

    def post(self):
        first_name = self.request.get('first-name')
        last_name = self.request.get('last-name')
        email = self.request.get('email')
        user_name = email
        password = self.request.get('password')
        
        unique_properties = ['email']
        user_data = self.user_model.create_user(user_name, unique_properties,
            email=email, password_raw=password, first_name=first_name, last_name=last_name, pw=password)
        if not user_data[0]: #user_data is a tuple
            self.response.write('Unable to create user for email %s because of duplicate keys %s' % (user_name, user_data[1]))
            return
        user = user_data[1]

        new_application = Application(parent=user.key)
        new_application.put()
        self.redirect('/application')
