import logging
from flask import request, render_template
from google.cloud import ndb
from admin.auth.login_manager import admin_login_required, get_current_admin_user
from common.models import Settings
from dkc.auth.models import AuthToken, UniqueUserTracking, User
from dkc.application.files_delete import delete_referenced_gcs_object
from dkc.application.models import GCSObjectReference, Application
from . import query_helpers
from . import dashboard_bp

logger = logging.getLogger(__name__)


@dashboard_bp.route("/danger_delete_applicants", methods=["GET", "POST"])
@admin_login_required
def delete_applicant():
    if request.method == "POST":
        handle_post()

    settings = Settings.get_config()
    all_applicants, all_applications = query_helpers.get_all_overview()
    template_values = {
        "all_applicants": all_applicants,
        "all_applications": all_applications,
        "admin_url": "/admin/danger_delete_applicants",
        "settings": settings,
        "current_admin_user": get_current_admin_user(),
    }
    return render_template("admin_dashboard/delete.html", **template_values)


def handle_post():
    emails_to_delete = request.form.getlist("email")
    logger.info("Deleting... %s", emails_to_delete)

    for email in emails_to_delete:
        applicant = query_helpers.find_applicant_by_email(email)
        if not applicant:
            logger.warning("Could not find applicant with email: %s", email)
            continue
        delete_applicant_completely(applicant.key)


@ndb.transactional(xg=True)
def delete_applicant_completely(applicant_key):
    applicant = applicant_key.get()
    application_key = applicant.application
    unique_user_tracking_key = ndb.Key(
        UniqueUserTracking, applicant._get_unique_attributes_id()
    )
    auth_token_keys = [
        tkey for tkey in AuthToken.query(ancestor=applicant_key).fetch(keys_only=True)
    ]
    gcs_obj_ref_keys = []
    if application_key:
        gcs_obj_ref_keys = [
            rkey
            for rkey in GCSObjectReference.query(ancestor=application_key).fetch(
                keys_only=True
            )
        ]
    for gcs_obj_ref in ndb.get_multi(gcs_obj_ref_keys):
        delete_referenced_gcs_object(gcs_obj_ref)
    keys_to_delete = (
        [applicant_key, unique_user_tracking_key]
        + ([application_key] if application_key else [])
        + auth_token_keys
        + gcs_obj_ref_keys
    )
    deleted_ack = ndb.delete_multi(keys_to_delete)
    logger.debug("Deleted %s keys", len(deleted_ack))
    logger.info("Deleted applicant: %s", applicant.email)
