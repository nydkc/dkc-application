import os, webapp2, jinja2
from google.appengine.api import users
from manage import *
from admin import OverviewHandler
from search import SearchHandler
from lists import ListsHandler
from show import ShowHandler

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
    ('/admin/overview', OverviewHandler),
    ('/admin/search', SearchHandler),
    ('/admin/lists', ListsHandler),
    ('/admin/show/([^/]+)?', ShowHandler),
    ('/admin.*', MainPage)
], debug=True)
