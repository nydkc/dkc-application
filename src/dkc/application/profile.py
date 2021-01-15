import logging
from flask import render_template, request
from flask_login import current_user, login_required
from google.cloud import ndb
from common.models import Settings
from . import application_bp


@application_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    settings = ndb.Key(Settings, "config").get()
    applicant = current_user
    application = applicant.application.get()

    if request.method == "POST":
        handle_post(applicant, application)

    template_values = {
        "applicant": applicant,
        "application": application,
        "application_url": "/application/profile",
        "settings": settings,
    }
    return render_template("application/profile.html", **template_values)


def handle_post(applicant, application):
    if application.submit_time:
        logging.info(
            "Attempt to modify profile by %s after submission", applicant.email
        )
        return

    applicant.first_name = request.form.get("first-name")
    applicant.last_name = request.form.get("last-name")
    application.grade = request.form.get("grade")
    application.address = request.form.get("address")
    application.city = request.form.get("city")
    application.zip_code = request.form.get("zip-code")
    application.phone_number = request.form.get("phone-number")
    application.division = request.form.get("division")
    application.ltg = request.form.get("ltg")
    application.school = request.form.get("school")
    application.school_address = request.form.get("school-address")
    application.school_city = request.form.get("school-city")
    application.school_zip_code = request.form.get("school-zip-code")
    application.club_president = request.form.get("club-president")
    application.club_president_phone_number = request.form.get(
        "club-president-phone-number"
    )
    application.faculty_advisor = request.form.get("faculty-advisor")
    application.faculty_advisor_phone_number = request.form.get(
        "faculty-advisor-phone-number"
    )
    ndb.put_multi([applicant, application])
