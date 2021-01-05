from flask import render_template
from google.cloud import ndb
from . import application_bp

# class ApplicationPersonalStatement(BaseHandler):

#     @user_required
#     def get(self):
#         self._serve_page()

#     @user_required
#     def post(self):
#         application_key = ndb.Key(urlsafe=self.request.get('form-key'))
#         application = application_key.get()

#         if application.submit_time:
#             logging.info("Attempt to modify personal statement by %s", applicant.email)
#             self._serve_page()
#             return

#         application.personal_statement_choice = self.request.get("personal-statement-choice")
#         application.personal_statement = self.request.get('personal-statement')
#         application.put()
#         self._serve_page()

#     def _serve_page(self):
#         template_values = {
#             'application_url': '/application/personal-statement'
#         }
#         self.render_application('application-personal_statement.html', template_values)


@application_bp.route("/personal-statement", methods=["GET", "POST"])
def personal_statement():
    settings = {
        "due_date": 2020,
    }
    applicant = {}
    application = {}
    template_values = {
        "settings": settings,
        "applicant": applicant,
        "application": application,
    }
    return render_template("application/personal-statement.html", **template_values)
