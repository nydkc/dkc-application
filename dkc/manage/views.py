import os, webapp2, jinja2
from google.appengine.api import users
from dkc.manage import *
from dkc.manage.admin import *
from dkc.manage.show import ShowHandler

class MainPage(webapp2.RequestHandler):

    def get(self):
        if users.get_current_user():
            self.redirect('/admin/overview')
        else:
            template_values = {
                "login_url": users.create_login_url('/admin/overview')
            }
            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.out.write(template.render(template_values))

application = webapp2.WSGIApplication([
    ('/admin/overview', AdminOverviewHandler),
    ('/admin/search', AdminSearchHandler),
    ('/admin/show/([^/]+)?', ShowHandler),
    ('/admin.*', MainPage)
], debug=True)
