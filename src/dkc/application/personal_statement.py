import logging
from flask import render_template, request
from flask_login import current_user, login_required
from google.cloud import ndb
from common.models import Settings
from . import application_bp

logger = logging.getLogger(__name__)


@application_bp.route("/personal-statement", methods=["GET", "POST"])
@login_required
def personal_statement():
    settings = ndb.Key(Settings, "config").get()
    applicant = current_user
    application = applicant.application.get()

    if request.method == "POST":
        handle_post(applicant, application)

    template_values = {
        "applicant": applicant,
        "application": application,
        "application_url": "/application/personal-statement",
        "settings": settings,
    }
    return render_template("application/personal_statement.html", **template_values)


def handle_post(applicant, application):
    if application.submit_time:
        logger.warning(
            "Attempt to modify personal statement by %s after submission",
            applicant.email,
        )
        return

    application.personal_statement_choice = request.form.get(
        "personal-statement-choice"
    )
    application.personal_statement = request.form.get("personal-statement")
    application.put()
