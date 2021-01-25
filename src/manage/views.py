# import os, webapp2, jinja2
# from google.appengine.api import users
# from manage import *
# from admin import OverviewHandler
# from search import SearchHandler
# from lists import ListsHandler
# from show import ShowHandler
# from settings import SettingsHandler
# from run_query import QueryHandler
# from deleted_files import DeletedFilesHandler, DeleteDeletedFilesHandler
# from delete import DeleteAccountHandler, DeleteAccountsByYearHandler

# class MainPage(webapp2.RequestHandler):

#     def get(self):
#         if users.get_current_user():
#             self.redirect('/admin/overview')
#         else:
#             template_values = {
#                 "login_url": users.create_login_url('/admin/overview')
#             }
#             template = JINJA_ENVIRONMENT.get_template('index.html')
#             self.response.out.write(template.render(template_values))

# class LogoutHandler(webapp2.RequestHandler):

#     def get(self):
#         template_values = {}
#         if users.get_current_user():
#             template_values['logout_url'] = users.create_logout_url('/admin')
#         template = JINJA_ENVIRONMENT.get_template('logout.html')
#         self.response.out.write(template.render(template_values))

# application = webapp2.WSGIApplication([
#     ('/admin/overview', OverviewHandler),
#     ('/admin/search', SearchHandler),
#     ('/admin/lists', ListsHandler),
#     ('/admin/show/([^/]+)?', ShowHandler),
#     ('/admin/settings', SettingsHandler),
#     ('/admin/logout', LogoutHandler),
#     ('/admin/query', QueryHandler),
#     ('/admin/deleted_files/delete/([^/]+)?', DeleteDeletedFilesHandler),
#     ('/admin/deleted_files', DeletedFilesHandler),
#     ('/admin/delete/account', DeleteAccountHandler),
#     ('/admin/delete/accountyear', DeleteAccountsByYearHandler),
#     ('/admin.*', MainPage)
# ], debug=True)

from manage.index import index_bp
from manage.auth.views import auth_bp

def register_blueprints_to(app):
    app.register_blueprint(index_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/admin')
