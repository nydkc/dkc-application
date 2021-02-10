import logging
from flask import abort, render_template, request
from flask_login import current_user, login_required
from google.cloud import ndb
from common.models import Settings
from . import application_bp

logger = logging.getLogger(__name__)


@application_bp.route("/involvement", methods=["GET", "POST"])
@login_required
def involvement():
    settings = ndb.Key(Settings, "config").get()
    applicant = current_user
    application = applicant.application.get()

    if request.method == "POST":
        handle_post(applicant, application)

    template_values = {
        "applicant": applicant,
        "application": application,
        "application_url": "/application/involvement",
        "settings": settings,
    }
    return render_template("application/involvement.html", **template_values)


def handle_post(applicant, application):
    if application.submit_time:
        logger.warning(
            "Attempt to modify involvement by %s after submission",
            applicant.email,
        )
        return abort(409)

    application.key_club_week_mon = request.form.get("key-club-week-monday")
    application.key_club_week_tue = request.form.get("key-club-week-tuesday")
    application.key_club_week_wed = request.form.get("key-club-week-wednesday")
    application.key_club_week_thu = request.form.get("key-club-week-thursday")
    application.key_club_week_fri = request.form.get("key-club-week-friday")

    application.attendance_dtc = request.form.get("attendance-dtc") == "on"
    application.attendance_fall_rally = (
        request.form.get("attendance-fall-rally") == "on"
    )
    application.attendance_kamp_kiwanis = (
        request.form.get("attendance-kamp-kiwanis") == "on"
    )
    application.attendance_key_leader = (
        request.form.get("attendance-key-leader") == "on"
    )
    application.attendance_ltc = request.form.get("attendance-ltc") == "on"
    application.attendance_icon = request.form.get("attendance-icon") == "on"

    application.positions = request.form.get("positions")

    application.put()
