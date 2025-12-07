import logging
from flask import abort, request, render_template, url_for
from flask_wtf import FlaskForm
from google.cloud import ndb
from common.flask_error_handlers import client_error_handler
from dkc.auth.models import AuthToken
from . import application_verification_bp

logger = logging.getLogger(__name__)


class VerificationForm(FlaskForm):
    pass


class VerificationAuthTokenError(Exception):
    def __init__(self, code):
        self.code = code


@application_verification_bp.app_errorhandler(VerificationAuthTokenError)
def verification_error_handler(e):
    return render_template("verification/error.html"), e.code


def decode_auth_token_with_type(urlsafe_token_key: str, auth_type: str) -> AuthToken:
    try:
        token_key = ndb.Key(urlsafe=urlsafe_token_key.encode("utf-8"))
        token = token_key.get()
    except:
        logger.error("Could not decode AuthToken key %s", urlsafe_token_key)
        raise VerificationAuthTokenError(400)
    if not isinstance(token, AuthToken):
        logger.error(
            "Attempted to access non-AuthToken key %s of type %s",
            token_key,
            type(token),
        )
        raise VerificationAuthTokenError(400)
    elif token.type != auth_type:
        # Token type must match, otherwise this is a misused token
        logger.error("Attemped to misuse AuthToken with type: %s", token.type)
        return abort(403)
    else:
        return token


@application_verification_bp.route("/v/<string:token_key>")
def external_verification(token_key: str):
    token = decode_auth_token_with_type(token_key, "v")
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
        template_values["is_already_verified"] = application.verification_ltg
        return render_template("verification/verification-ltg.html", **template_values)
    elif application.verification_club_president_token == token.key:
        template_values["is_already_verified"] = application.verification_club_president
        return render_template(
            "verification/verification-club-president.html", **template_values
        )
    elif application.verification_faculty_advisor_token == token.key:
        template_values["is_already_verified"] = (
            application.verification_faculty_advisor
        )
        return render_template(
            "verification/verification-faculty-advisor.html", **template_values
        )
    else:
        return render_template("verification/error.html")


@application_verification_bp.route("/v/<string:token_key>/agree", methods=["POST"])
def external_verification_agree(token_key: str):
    token = decode_auth_token_with_type(token_key, "v")
    form = VerificationForm()
    if not form.validate():
        raise VerificationAuthTokenError(403)

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
    # We choose not to delete the token since it seems that verifiers want to
    # view the application even after approval.
    # token_key.delete()
