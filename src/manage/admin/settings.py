import logging
from datetime import datetime
from flask import render_template, request
from google.cloud import ndb
from common.jinja_functions import datetimeformat
from common.models import Settings
from common.timezone import UTC, Eastern
from manage.admin_auth.login_manager import admin_login_required, get_current_admin_user
from . import admin_bp

logger = logging.getLogger(__name__)


@admin_bp.route("/settings", methods=["GET", "POST"])
@admin_login_required
def settings():
    settings = ndb.Key(Settings, "config").get()

    if request.method == "POST":
        handle_post(settings)

    template_values = {
        "current_time": datetime.now(),
        "settings": settings,
        "admin_url": "/admin/settings",
        "current_admin_user": get_current_admin_user(),
    }
    return render_template("admin/settings.html", **template_values)


def handle_post(settings):
    due_date = parse_html_datetime_local(request.form.get("due_date"))
    # Recognize as Eastern TZ Offset
    due_date = due_date.replace(tzinfo=Eastern)
    # Cloud Datastore only supports timezone-naive datetime objects
    settings.due_date = due_date.astimezone(tz=UTC())

    settings.awards_booklet_url = request.form.get("awards_booklet_url").strip()

    settings.secret_key = request.form.get("secret_key")

    settings.google_oauth_client_id = request.form.get("google_oauth_client_id").strip()
    settings.google_oauth_client_secret = request.form.get(
        "google_oauth_client_secret"
    ).strip()

    settings.recaptcha_site_key = request.form.get("recaptcha_site_key").strip()
    settings.recaptcha_secret = request.form.get("recaptcha_secret").strip()

    settings.sendgrid_api_key = request.form.get("sendgrid_api_key").strip()

    settings.gcs_bucket = request.form.get("gcs_bucket").strip()

    settings.put()


def parse_html_datetime_local(value):
    try:
        # Attempt to parse with seconds first. However, the browser drops
        # the seconds part when it is 00.
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
    except ValueError as e:
        logger.error("Datetime parsing error (%s) on invalid due date: %s", e, value)

    try:
        # Attempt to parse without seconds.
        return datetime.strptime(value, "%Y-%m-%dT%H:%M")
    except ValueError as e:
        logger.error("Datetime parsing error (%s) on invalid due date: %s", e, value)

    # Return minimum value if datetime could not be parsed.
    return datetime.min
