from flask import render_template
from flask_login import current_user, login_required
from google.cloud import ndb
from common.models import Settings
from . import application_bp


@application_bp.route("/")
@application_bp.route("/overview")
@login_required
def overview():
    settings = ndb.Key(Settings, "config").get()
    applicant = current_user
    application = current_user.application.get()
    user_id = current_user.key.id()
    template_values = {
        "applicant": applicant,
        "application": application,
        "user_id": user_id,
        "application_url": "/application/overview",
        "settings": settings,
    }
    return render_template("application/overview.html", **template_values)
