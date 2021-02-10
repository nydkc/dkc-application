import logging
from flask import abort, request, render_template, url_for
from flask_wtf import FlaskForm
from google.cloud import ndb
from dkc.auth.models import AuthToken
from . import verify_bp

logger = logging.getLogger(__name__)


class VerificationForm(FlaskForm):
    pass


@verify_bp.route("/v/<string:token_key>")
def external_verification(token_key: str):
    try:
        token = ndb.Key(urlsafe=token_key.encode("utf-8")).get()
    except:
        logger.error("Could not decode key %s", token_key)
        return render_template("verification/error.html"), 400
    if not isinstance(token, AuthToken):
        logger.error(
            "Attempted to access non-AuthToken key %s of type %s",
            token_key,
            type(token),
        )
        return render_template("verification/error.html"), 403

    form = VerificationForm()

    application = token.key.parent().get()
    applicant = application.key.parent().get()
    user_id = applicant.key.id()
    template_values = {
        "applicant": applicant,
        "application": application,
        "user_id": user_id,
        "verification_agree_url": url_for(
            ".external_verification_agree", token_key=token_key
        ),
        "token_key": token_key,
        "form": form,
    }
    if application.verification_ltg_token == token.key:
        return render_template("verification/verification-ltg.html", **template_values)
    elif application.verification_club_president_token == token.key:
        return render_template(
            "verification/verification-club-president.html", **template_values
        )
    elif application.verification_faculty_advisor_token == token.key:
        return render_template(
            "verification/verification-faculty-advisor.html", **template_values
        )
    else:
        return render_template("verification/error.html")


@verify_bp.route("/v/<string:token_key>/agree", methods=["POST"])
def external_verification_agree(token_key: str):
    try:
        token = ndb.Key(urlsafe=token_key.encode("utf-8")).get()
    except:
        logger.error("Could not decode key %s", token_key)
        return render_template("verification/error.html"), 400
    if not isinstance(token, AuthToken):
        logger.error(
            "Attempted to access non-AuthToken key %s of type %s",
            token_key,
            type(token),
        )
        return render_template("verification/error.html"), 403

    form = VerificationForm()
    if not form.validate():
        return render_template("verification/error.html"), 403

    # Check that the token corresponds to the application without performing any
    # modifications. Modifications are performed in a transaction.
    application = token.key.parent().get()
    if not (
        application.verification_ltg_token == token.key
        or application.verification_club_president_token == token.key
        or application.verification_faculty_advisor_token == token.key
    ):
        return render_template("verification/error.html")
    add_verification_from_token(application.key, token.key)

    applicant = application.key.parent().get()
    template_values = {
        "applicant": applicant,
    }
    return render_template("verification/success.html", **template_values)


@ndb.transactional()
def add_verification_from_token(application_key, token_key):
    application = application_key.get()
    if application.verification_ltg_token == token_key:
        application.verification_ltg = True
    elif application.verification_club_president_token == token_key:
        application.verification_club_president = True
    elif application.verification_faculty_advisor_token == token_key:
        application.verification_faculty_advisor = True
    else:
        return
    application.put()
    token_key.delete()
