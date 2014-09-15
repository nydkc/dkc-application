import os, webapp2, jinja2
from dkc import *
from models import *

class ApplicationPage(BaseHandler):

    @user_required
    def get(self):
        self.render_template('application.html')
