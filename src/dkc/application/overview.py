from flask import render_template
from google.cloud import ndb
from . import application_bp

# class ApplicationOverview(BaseHandler):

#     @user_required
#     def get(self):
#         self._serve_page()

#     @user_required
#     def post(self):
#         self._serve_page()

#     def _serve_page(self):
#         config = ndb.Key(Settings, 'config').get()
#         template_values = {
#             'user_id': self.user.get_id(),
#             'application_url': '/application/overview',
#             'config': config,
#         }
#         self.render_application('application-overview.html', template_values)


@application_bp.route("/")
def overview():
    settings = {
        "due_date": 2020,
    }
    template_values = {
        "settings": settings,
    }
    return render_template('application/overview.html', **template_values)
