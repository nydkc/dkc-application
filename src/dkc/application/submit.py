import json
import logging
from datetime import datetime
from flask import abort, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from google.cloud import ndb
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    CustomArg,
    From,
    HtmlContent,
    Mail,
    Subject,
    To,
)
from common.models import Settings
from . import application_bp


@application_bp.route("/submit", methods=["GET", "POST"])
@login_required
def submit():
    applicant = current_user
    application = applicant.application.get()

    if request.method == "POST":
        handle_post(applicant, application)

    user_id = applicant.key.id()
    template_values = {
        "applicant": applicant,
        "application": application,
        "user_id": user_id,
        "application_url": "/application/submit",
        **check_submission_incomplete_status(applicant, application),
    }
    return render_template("application/submit.html", **template_values)


def handle_post(applicant, application):
    if application.submit_time:
        logging.info(
            "Attempt to submit by %s after submission",
            applicant.email,
        )
        return

    incomplete_status = check_submission_incomplete_status(applicant, application)
    if True in incomplete_status.values():
        return abort(400, description="You application is not complete!")

    application.submit_time = datetime.now()
    send_submission_confirmation_email(applicant, application)
    application.put()


def send_submission_confirmation_email(applicant, application):
    settings = ndb.Key(Settings, "config").get()
    template_values = {
        "applicant": applicant,
        "application": application,
        "settings": settings,
    }
    email_html = render_template(
        "application/submit-confirmation-email.html", **template_values
    )

    settings = ndb.Key(Settings, "config").get()
    sg = SendGridAPIClient(api_key=settings.sendgrid_api_key)
    message = Mail(
        from_email=From("recognition@nydkc.org", "NYDKC Awards Committee"),
        to_emails=To(applicant.email),
        subject=Subject(
            "DKC Application Submission Confirmation for {} {}".format(
                applicant.first_name, applicant.last_name
            )
        ),
        html_content=HtmlContent(email_html),
    )
    message.custom_arg = [
        CustomArg(
            key="dkc_application_key", value=application.key.urlsafe().decode("utf-8")
        ),
        CustomArg(key="dkc_purpose", value="submission_confirmation"),
    ]

    response = sg.client.mail.send.post(request_body=message.get())
    if response.status_code != 202:
        json_response = json.loads(response.body)
        logging.error(
            "Error sending email to %s: %s", message.to, json_response["errors"]
        )
        return abort(503)


def check_submission_incomplete_status(applicant, application):
    def is_empty_or_none(f):
        if isinstance(f, list):
            return len(f) == 0
        if isinstance(f, str):
            return f == ""
        return f is None

    # Profile is incomplete if any fields are empty
    is_profile_incomplete = any(
        map(
            is_empty_or_none,
            [
                applicant.first_name,
                applicant.last_name,
                application.grade,
                # application.address,
                # application.city,
                # application.zip_code,
                # application.phone_number,
                application.division,
                application.ltg,
                application.school,
                # application.school_address,
                # application.school_city,
                # application.school_zip_code,
                application.club_president,
                application.club_president_phone_number,
                application.faculty_advisor,
                application.faculty_advisor_phone_number,
            ],
        )
    )

    # Personal statement is incomplete if any fields are empty
    is_personal_statement_incomplete = any(
        map(
            is_empty_or_none,
            [
                application.personal_statement_choice,
                application.personal_statement,
            ],
        )
    )

    # Projects is incomplete if all fields are empty
    is_projects_incomplete = all(
        map(
            is_empty_or_none,
            [
                application.international_projects,
                application.district_projects,
                application.divisionals,
                application.division_projects,
                application.scoring_reason_two,
            ],
        )
    )

    # Involvement is incomplete if all fields are empty
    is_involvement_incomplete = all(
        map(
            is_empty_or_none,
            [
                application.key_club_week_mon,
                application.key_club_week_tue,
                application.key_club_week_wed,
                application.key_club_week_thu,
                application.key_club_week_fri,
                application.attendance_dtc,
                application.attendance_fall_rally,
                application.attendance_kamp_kiwanis,
                application.attendance_key_leader,
                application.attendance_ltc,
                application.attendance_icon,
                application.positions,
                application.scoring_reason_three,
            ],
        )
    )

    # Activities is incomplete if all fields are empty
    # or if newsletter/website submission is checked and there are no files attached
    is_activities_incomplete = all(
        map(
            is_empty_or_none,
            [
                application.kiwanis_one_day,
                application.k_family_projects,
                application.interclub_projects,
                application.advocacy_cause,
                application.advocacy_description,
                application.committee,
                application.committee_type,
                application.committee_description,
                application.divisional_newsletter,
                application.divisional_newsletter_info,
                application.district_newsletter,
                application.district_newsletter_info,
                application.district_website,
                application.district_website_info,
                application.other_projects,
                application.scoring_reason_four,
            ],
        )
    ) or (
        (
            application.divisional_newsletter
            or application.district_newsletter
            or application.district_website
        )
        and is_empty_or_none(application.newsletter_materials)
    )

    # Other is incomplete if any fields are empty
    # or if recommendation is checked and there are no files attached
    is_other_incomplete = any(
        map(
            is_empty_or_none,
            [
                application.outstanding_awards,
            ],
        )
    ) or (
        application.recommender_points != "No Recommendation"
        and is_empty_or_none(application.other_materials)
    )

    # Verification is incomplete if we have fewer than 2 external parties,
    # or if we don't have the applicant's own verification
    verification_count = 0
    if application.verification_ltg:
        verification_count += 1
    if application.verification_club_president:
        verification_count += 1
    if application.verification_faculty_advisor:
        verification_count += 1
    is_verification_incomplete = (
        verification_count < 2 or not application.verification_applicant
    )

    return {
        "is_profile_incomplete": is_profile_incomplete,
        "is_personal_statement_incomplete": is_personal_statement_incomplete,
        "is_projects_incomplete": is_projects_incomplete,
        "is_involvement_incomplete": is_involvement_incomplete,
        "is_activities_incomplete": is_activities_incomplete,
        "is_other_incomplete": is_other_incomplete,
        "is_verification_incomplete": is_verification_incomplete,
    }
