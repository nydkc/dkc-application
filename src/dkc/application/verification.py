import logging
from datetime import datetime
from flask import abort, render_template, request, url_for
from flask_login import current_user, login_required
from google.cloud import ndb
from common.constants import AUTH_TOKEN_VALIDITY_DAYS
from common.email_provider import (
    get_email_provider,
    Email,
    Subject,
    HtmlContent,
    CustomArgs,
)
from common.models import Settings
from dkc.auth.models import AuthToken
from . import application_bp

logger = logging.getLogger(__name__)


@application_bp.route("/verification", methods=["GET", "POST"])
@login_required
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
        "auth_token_validity_days": AUTH_TOKEN_VALIDITY_DAYS,
        "settings": settings,
    }
    return render_template("application/verification.html", **template_values)


def handle_post(applicant, application):
    if application.submit_time:
        logger.warning(
            "Attempt to modify verification by %s after submission",
            applicant.email,
        )
        return abort(409)

    if profile_has_invalid_fields(applicant, application):
        logger.warning(
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
            # delete the previous LTG token
            if application.verification_ltg_token:
                application.verification_ltg_token.delete()
            application.verification_ltg_token = token_key
            application.verification_ltg_sent = True
            verifier_email = application.verification_ltg_email
            verifier_name = f"Lieutenant Governor {application.ltg.title()}"
        elif task == "club-president" and not application.verification_club_president:
            application.verification_club_president_email = request.form.get(
                "club-president-email"
            )
            # delete the previous club president token
            if application.verification_club_president_token:
                application.verification_club_president_token.delete()
            application.verification_club_president_token = token_key
            application.verification_club_president_sent = True
            verifier_name = f"Club President {application.club_president.title()}"
            verifier_email = application.verification_club_president_email
        elif task == "faculty-advisor" and not application.verification_faculty_advisor:
            application.verification_faculty_advisor_email = request.form.get(
                "faculty-advisor-email"
            )
            # delete the previous faculty advisor token
            if application.verification_faculty_advisor_token:
                application.verification_faculty_advisor_token.delete()
            application.verification_faculty_advisor_token = token_key
            application.verification_faculty_advisor_sent = True
            verifier_name = f"Faculty Advisor {application.faculty_advisor.title()}"
            verifier_email = application.verification_faculty_advisor_email
        else:
            logger.warning(
                "Invalid verification task for %s: %s", applicant.email, task
            )
            return abort(400, description="Invalid verification task")
        send_verification_email(
            applicant, application, token_key, verifier_name, verifier_email
        )

    application.put()


def create_verification_auth_token(application):
    # Make call to allocate_ids to get randomly generated IDs
    key = AuthToken.allocate_ids(parent=application.key, size=1)[0]
    token = AuthToken(key=key, type="v")
    token_key = token.put()
    return token_key


def send_verification_email(
    applicant, application, token_key, recipient_name, recipient_email
):
    settings = ndb.Key(Settings, "config").get()
    verification_url = url_for(
        "application_verification.external_verification",
        token_key=token_key.urlsafe().decode("utf-8"),
        _external=True,
    )
    logger.debug(
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
    email_provider = get_email_provider(settings)
    response = email_provider.send_email(
        from_email=Email(email="recognition@nydkc.org", name="NYDKC Awards Committee"),
        to_email=Email(email=recipient_email),
        subject=Subject(
            line=(
                f"Please verify Distinguished Key Clubber Application for {applicant.first_name} {applicant.last_name}"
            )
        ),
        html_content=HtmlContent(content=email_html),
        custom_args=CustomArgs(
            metadata=(
                {
                    "dkc_application_key": application.key.urlsafe().decode("utf-8"),
                    "dkc_purpose": "verification",
                }
            )
        ),
    )
    if not response.success:
        logger.error("Error sending email to %s: %s", recipient_email, response.errors)
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
