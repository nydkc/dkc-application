import io
import os
import logging
from flask import abort, render_template, request, send_file
from flask_login import current_user
from google.cloud import ndb
from common.models import Settings
from common.util import generate_pdf
from dkc.auth.models import User, AuthToken
from manage.auth.login_manager import get_current_admin_user
from . import application_bp


def check_access(applicant_key, token_key):
    """Checks that the token key or current user can view the application."""
    if token_key:
        try:
            token_key = ndb.Key(urlsafe=token_key.encode("utf-8"))
            token = token_key.get()
        except:
            logging.error("Could not decode key %s", token_key)
            return abort(400, description="Invalid token")
        if not isinstance(token, AuthToken):
            logging.error(
                "Attempted to access non-AuthToken key %s of type %s",
                token_key,
                type(token),
            )
            return abort(403)
        # Check that token matches that of the application to download
        if applicant_key != token_key.parent().parent():
            return abort(403)
    elif get_current_admin_user() is not None:
        # Allow admin access to all applications
        logging.info(
            "Admin %s is viewing application of %s",
            get_current_admin_user().email,
            applicant_key,
        )
        return
    elif current_user is None or not current_user.is_authenticated:
        # Anonymous access is not allowed
        logging.error(
            "Anonymous user denied access to application of %s", applicant_key
        )
        return abort(401)
    elif current_user.key != applicant_key:
        # Cannot access another user's application
        logging.error(
            "User %s denied access to application of %s",
            current_user.key,
            applicant_key,
        )
        return abort(403)


@application_bp.route("/download/pdf/<int:user_id>-<string:name>.pdf")
def download_pdf(user_id, name):
    applicant_key = ndb.Key(User, user_id)
    token_key = request.args.get("t")
    check_access(applicant_key, token_key)

    applicant = applicant_key.get()
    application = applicant.application.get()
    settings = ndb.Key(Settings, "config").get()
    template_values = {
        "settings": settings,
        "applicant": applicant,
        "application": application,
        # TODO: use a more pythonic way of getting to the static dir (maybe using flask?)
        "STATIC_DIR": os.path.normpath(
            os.path.join(os.path.dirname(__file__), "../../static")
        ),
    }
    filename = "{}.pdf".format(name)
    return send_file(
        io.BytesIO(generate_pdf(render_template("pdf/pdf.html", **template_values))),
        attachment_filename=filename,
    )


@application_bp.route("/download/html/<int:user_id>-<string:name>.<string:ext>")
def download_html(user_id, name, ext):
    applicant_key = ndb.Key(User, user_id)
    token_key = request.args.get("t")
    check_access(applicant_key, token_key)

    applicant = applicant_key.get()
    application = applicant.application.get()
    settings = ndb.Key(Settings, "config").get()
    template_values = {
        "settings": settings,
        "applicant": applicant,
        "application": application,
        # TODO: use a more pythonic way of getting to the static dir (maybe using flask?)
        "STATIC_DIR": "",
    }
    filename = "{}.pdf".format(name)
    return render_template("pdf/pdf.html", **template_values)
