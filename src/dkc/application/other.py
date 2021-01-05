from flask import render_template
from google.cloud import ndb
from . import application_bp

# class ApplicationOther(BaseHandler):

#     @user_required
#     def get(self):
#         self._serve_page()

#     @user_required
#     def post(self):
#         application_key = ndb.Key(urlsafe=self.request.get('form-key'))
#         application = application_key.get()

#         if application.submit_time:
#             logging.info("Attempt to modify scoring by %s", applicant.email)
#             self._serve_page()
#             return

#         if self.request.get('early-submission-checkbox'):
#             application.early_submission_points = self.request.get('early-submission-points')
#         else:
#             application.early_submission_points = "Any section"

#         if self.request.get('recommender-checkbox'):
#             application.recommender_points = self.request.get('recommender-points')
#         else:
#             application.recommender_points = "No Recommendation"

#         application.outstanding_awards = self.request.get('outstanding-awards')

#         application.scoring_reason_two = self.request.get('scoring-reason-two')
#         application.scoring_reason_three = self.request.get('scoring-reason-three')
#         application.scoring_reason_four = self.request.get('scoring-reason-four')

#         application.put()
#         self._serve_page()

#     def _serve_page(self):
#         config = ndb.Key(Settings, 'config').get()
#         template_values = {
#             'application_url': '/application/other',
#             'config': config
#         }
#         self.render_application('application-other.html', template_values)


@application_bp.route("/other", methods=["GET", "POST"])
def other():
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
    return render_template("application/other.html", **template_values)
