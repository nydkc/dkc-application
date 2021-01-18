import logging
from flask import render_template, request
from flask_login import current_user, login_required
from google.cloud import ndb
from common.models import Settings
from . import application_bp


@application_bp.route("/other", methods=["GET", "POST"])
@login_required
def other():
    settings = ndb.Key(Settings, "config").get()
    applicant = current_user
    application = applicant.application.get()

    if request.method == "POST":
        handle_post(applicant, application)

    template_values = {
        "applicant": applicant,
        "application": application,
        "application_url": "/application/other",
        "settings": settings,
    }
    return render_template("application/other.html", **template_values)


def handle_post(applicant, application):
    if application.submit_time:
        logging.info(
            "Attempt to modify other section by %s after submission",
            applicant.email,
        )
        return

    if request.form.get("early-submission-checkbox"):
        application.early_submission_points = request.form.get(
            "early-submission-points"
        )
    else:
        application.early_submission_points = "Any section"

    if request.form.get("recommender-checkbox"):
        application.recommender_points = request.form.get("recommender-points")
    else:
        application.recommender_points = "No Recommendation"

    application.outstanding_awards = request.form.get("outstanding-awards")

    application.scoring_reason_two = request.form.get("scoring-reason-two")
    application.scoring_reason_three = request.form.get("scoring-reason-three")
    application.scoring_reason_four = request.form.get("scoring-reason-four")

    application.put()
