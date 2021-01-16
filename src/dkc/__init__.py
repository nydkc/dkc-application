# import os, webapp2, jinja2
# from webapp2_extras import auth, sessions
# import webapp2_extras.appengine.auth.models
# from constants import *
# from models import *

# WEBAPP2_CONFIG = {
#     'webapp2_extras.auth': {
#         'user_model': 'dkc.models.User',
#         'user_attributes': ['email']
#     },
#     'webapp2_extras.sessions': {
#         'secret_key': PASSWORD_SECRET_KEY
#     }
# }

# def user_required(handler):
#     def check_login(self, *args, **kwargs):
#         auth = self.auth
#         if not auth.get_user_by_session():
#             self.redirect('/login')
#         else:
#             return handler(self, *args, **kwargs)
#     return check_login

# def guest_only(handler):
#     def check_login(self, *args, **kwargs):
#         auth = self.auth
#         if auth.get_user_by_session():
#             self.redirect('/application')
#         else:
#             return handler(self, *args, **kwargs)
#     return check_login

# class BaseHandler(webapp2.RequestHandler):

#     @webapp2.cached_property
#     def auth(self):
#         """Shortcut to access the auth instance as a property."""
#         return auth.get_auth()

#     @webapp2.cached_property
#     def user_info(self):
#         """Shortcut to access a subset of the user attributes that are stored
#         in the session.

#         The list of attributes to store in the session is specified in
#         WEBAPP2_CONFIG['webapp2_extras.auth']['user_attributes'].
#         :returns
#         A dictionary with most user information
#         """
#         return self.auth.get_user_by_session()

#     @webapp2.cached_property
#     def user(self):
#         """Shortcut to access the current logged in user.

#         Unlike user_info, it fetches information from the persistence layer and
#         returns an instance of the underlying model.

#         :returns
#         The instance of the user model associated to the logged in user.
#         """
#         u = self.user_info
#         return self.user_model.get_by_id(u['user_id']) if u else None

#     @webapp2.cached_property
#     def user_model(self):
#         """Returns the implementation of the user model.
#         It is consistent with WEBAPP2_CONFIG['webapp2_extras.auth']['user_model'], if set.
#         """
#         return self.auth.store.user_model

#     @webapp2.cached_property
#     def session(self):
#         return self.session_store.get_session(backend="datastore")

#     def render_template(self, template_filename, template_values={}):
#         user = self.user_info
#         template_values['user'] = user
#         template = JINJA_ENVIRONMENT.get_template(template_filename)
#         self.response.out.write(template.render(template_values))

#     def display_message(self, message):
#         template_values = {
#             'message': message
#         }
#         self.render_template('message.html', template_values)

#     def render_application(self, template_filename, template_values={}):
#         applicant = self.user
#         application_key = applicant.application
#         application = application_key.get()
#         template_values.update({
#             'applicant': applicant,
#             'application': application,
#             'form_key': application_key.urlsafe(),
#             'submitted': application.submit_time
#         })
#         self.render_template(template_filename, template_values)

#     # this is needed for webapp2 sessions to work
#     def dispatch(self):
#         self.session_store = sessions.get_store(request=self.request)
#         try:
#             webapp2.RequestHandler.dispatch(self)
#         finally:
#             self.session_store.save_sessions(self.response)

import jinja2
from common import jinja_functions

JINJA_OPTIONS = {
    "extensions": ["jinja2.ext.autoescape"],
}
ADDITIONAL_JINJA_FILTERS = {
    "datetimeformat": jinja_functions.datetimeformat,
    "byteconvert": jinja_functions.byteConversion,
    "to_file_info": jinja_functions.toFileInfo,
    "split_string": jinja_functions.splitString,
    "split_regex": jinja_functions.splitRegex,
    "highlight_search": jinja_functions.search,
    "getvars": jinja_functions.getVars,
}
# ADDITIONAL_JINJA_TESTS = {"still_early": jinja_functions.getEarlyStatus}
