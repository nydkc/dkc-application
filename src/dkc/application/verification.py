import json
import logging
from datetime import datetime
from flask import abort, render_template, request, url_for
from flask_login import current_user, login_required
from google.cloud import ndb
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Content,
    CustomArg,
    From,
    HtmlContent,
    Mail,
    Subject,
    To,
)
from common.models import Settings
from dkc.auth.models import AuthToken
from . import application_bp


@application_bp.route("/verification", methods=["GET", "POST"])
def verification():
    settings = ndb.Key(Settings, "config").get()
    applicant = current_user
    application = applicant.application.get()

    if request.method == "POST":
        handle_post(applicant, application)

    template_values = {
        "applicant": applicant,
        "application": application,
        "application_url": "/application/verification",
        "is_profile_invalid": profile_has_invalid_fields(applicant, application),
        "settings": settings,
    }
    return render_template("application/verification.html", **template_values)


def handle_post(applicant, application):
    if application.submit_time:
        logging.info(
            "Attempt to modify verification by %s after submission",
            applicant.email,
        )
        return

    if profile_has_invalid_fields(applicant, application):
        logging.warning(
            "Cannot send emails for %s without completed profile", applicant.email
        )
        return abort(400, description="Profile must be completed first.")

    task = request.form.get("task")
    if task == "applicant":
        application.verification_applicant = True
        application.verification_applicant_date = datetime.now()
    else:
        token_key = create_verification_auth_token(application)
        if task == "ltg" and not application.verification_ltg:
            application.verification_ltg_email = request.form.get("ltg-email")
            application.verification_ltg_token = token_key
            application.verification_ltg_sent = True
            verifier_email = application.verification_ltg_email
            verifier_name = "Lieutenant Governor " + application.ltg.title()
        elif task == "club-president" and not application.verification_club_president:
            application.verification_club_president_email = request.form.get(
                "club-president-email"
            )
            application.verification_club_president_token = token_key
            application.verification_club_president_sent = True
            verifier_name = "Club President " + application.club_president.title()
            verifier_email = application.verification_club_president_email
        elif task == "faculty-advisor" and not application.verification_faculty_advisor:
            application.verification_faculty_advisor_email = request.form.get(
                "faculty-advisor-email"
            )
            application.verification_faculty_advisor_token = token_key
            application.verification_faculty_advisor_sent = True
            verifier_name = "Faculty Advisor " + application.faculty_advisor.title()
            verifier_email = application.verification_faculty_advisor_email
        send_verification_email(
            applicant, application, token_key, verifier_name, verifier_email
        )

    application.put()


def create_verification_auth_token(application):
    token = AuthToken(parent=application.key, type="v")
    token_key = token.put()
    return token_key


def send_verification_email(
    applicant, application, token_key, recipient_name, recipient_email
):
    settings = ndb.Key(Settings, "config").get()
    verification_url = url_for(
        "verify.external_verification",
        token_key=token_key.urlsafe().decode("utf-8"),
        _external=True,
    )
    logging.debug(
        "Generated verification url for %s to verify application of %s",
        recipient_email,
        applicant.email,
    )

    template_values = {
        "applicant": applicant,
        "application": application,
        "settings": settings,
        "verification_url": verification_url,
        "verifier_name": recipient_name,
    }
    email_html = render_template(
        "application/verification-email.html", **template_values
    )

    settings = ndb.Key(Settings, "config").get()
    sg = SendGridAPIClient(api_key=settings.sendgrid_api_key)
    message = Mail(
        from_email=From("recognition@nydkc.org", "NYDKC Awards Committee"),
        to_emails=To(recipient_email),
        subject=Subject(
            "Please verify Distinguished Key Clubber Application for {} {}".format(
                applicant.first_name, applicant.last_name
            )
        ),
        html_content=HtmlContent(email_html),
    )
    message.add_custom_arg(
        CustomArg(key="application", value=application.key.urlsafe().decode("utf-8"))
    )

    response = sg.client.mail.send.post(request_body=message.get())
    if response.status_code != 202:
        json_response = json.loads(response.body)
        logging.error(
            "Error sending email to %s: %s", message.to, json_response["errors"]
        )
        return abort(503)


def profile_has_invalid_fields(applicant, application):
    def is_empty_or_none(f):
        return f == "" or f is None

    fields = [
        applicant.first_name,
        applicant.last_name,
        application.school,
        application.division,
        application.ltg,
        application.club_president,
        application.club_president_phone_number,
        application.faculty_advisor,
        application.faculty_advisor_phone_number,
    ]
    return any(map(is_empty_or_none, fields))
