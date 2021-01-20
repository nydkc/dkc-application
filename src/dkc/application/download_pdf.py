import io
import os
import logging
from flask import abort, render_template, request, send_file
from flask_login import current_user
from google.cloud import ndb
from dkc.util import generate_pdf
from dkc.auth.models import User, AuthToken
from common.models import Settings
from . import application_bp

#     def get(self, user_id,):
#         token = self.request.get("t")
#         token_id = self.request.get("a")
#         if token and token_id: # Used for verification bypass
#             user, ts = self.user_model.get_by_auth_token(int(token_id), token, 'signup')
#             if not user:
#                 logging.info('Could not verify token to view application with id "%s" and signup token "%s"', token_id, token)
#                 self.display_message("Invalid URL to view application!")
#                 return
#         elif users.get_current_user(): # Logged in to Google and connected with dkc-application
#             if not users.is_current_user_admin():
#                 logging.info('Non-admin access of aplication %s by %s', user_id, users.get_current_user().email())
#                 self.response.set_status(401);
#                 self.display_message("You are not an admin! Only admins are allowed to view applications.")
#                 return
#         else:
#             if self.user is None: # Prevent access from users not logged in
#                 logging.info("Unauthorized access of application %s", user_id)
#                 self.response.set_status(401);
#                 self.display_message("You are not authorized to view this application!")
#                 return
#             elif user_id != str(self.user_info['user_id']): # Prevent access from other users
#                 applicant = self.user
#                 logging.info("Attempted access of application %s by %s" % (user_id, applicant.email))
#                 self.response.set_status(401);
#                 self.display_message("%s %s, please do not attempt to access the applications of other applicants." % (applicant.first_name, applicant.last_name))
#                 return

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
    elif current_user is None or not current_user.is_authenticated:
        # Anonymous access is not allowed
        logging.error("Anonymous user denied access to application of %s", applicant_key)
        return abort(401)
    elif current_user.key != applicant_key:
        # Cannot access another user's application
        logging.error("User %s denied access to application of %s", current_user.key, applicant_key)
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
