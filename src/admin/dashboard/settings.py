import logging
from datetime import datetime
from flask import render_template, request
from google.cloud import ndb
from common.gcp import GCP_PROJECT_ID
from common.models import Settings
from common.timezone import UTC, Eastern
from admin.auth.login_manager import admin_login_required, get_current_admin_user
from . import dashboard_bp

logger = logging.getLogger(__name__)


@dashboard_bp.route("/settings", methods=["GET", "POST"])
@admin_login_required
def settings():
    settings = ndb.Key(Settings, "config").get()

    if request.method == "POST":
        handle_post(settings)

    template_values = {
        "current_time": datetime.now(),
        "settings": settings,
        "gcp_project_id": GCP_PROJECT_ID,
        "admin_url": "/admin/settings",
        "current_admin_user": get_current_admin_user(),
    }
    return render_template("admin_dashboard/settings.html", **template_values)


def handle_post(settings: Settings):
    due_date = parse_html_datetime_local(request.form.get("due_date"))
    # Cloud Datastore only supports timezone-naive datetime objects.
    settings.due_date = due_date.astimezone(tz=UTC()).replace(tzinfo=None)

    settings.awards_booklet_url = request.form.get("awards_booklet_url").strip()

    settings.secret_key = request.form.get("secret_key")

    settings.google_oauth_client_id = request.form.get("google_oauth_client_id").strip()
    settings.google_oauth_client_secret = request.form.get(
        "google_oauth_client_secret"
    ).strip()

    settings.recaptcha_site_key = request.form.get("recaptcha_site_key").strip()
    settings.recaptcha_secret = request.form.get("recaptcha_secret").strip()

    settings.sendgrid_api_key = request.form.get("sendgrid_api_key").strip()
    settings.mailersend_api_key = request.form.get("mailersend_api_key").strip()

    settings.gcs_bucket = request.form.get("gcs_bucket").strip()

    settings.put()


def parse_html_datetime_local(value: str) -> datetime:
    parsed_datetime = datetime.min
    try:
        # First, attempt to parse with seconds.
        parsed_datetime = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
    except ValueError as with_seconds_e:
        try:
            # If the browser drops the seconds, parse without seconds.
            # Note that some browsers drop the seconds part when it is 00.
            parsed_datetime = datetime.strptime(value, "%Y-%m-%dT%H:%M")
        except ValueError as without_seconds_e:
            logger.warning(
                "Datetime parsing errors on due date '%s'.\n[with seconds]: %s\n[without seconds]: %s",
                value,
                with_seconds_e,
                without_seconds_e,
            )

    # Recognize as Eastern TZ Offset
    parsed_datetime = parsed_datetime.replace(tzinfo=Eastern)
    return parsed_datetime
