import datetime
import logging
from flask import abort, current_app, redirect
from flask_login import current_user
from google.cloud import ndb, storage
from common.gcs import gcs, generate_signed_url_for
from common.timezone import Eastern
from admin.auth.login_manager import get_current_admin_user
from .models import GCSObjectReference
from . import application_bp

logger = logging.getLogger(__name__)


def decode_gcs_obj_ref(urlsafe_gcs_obj_ref_key: str) -> GCSObjectReference:
    try:
        gcs_obj_ref_key = ndb.Key(urlsafe=urlsafe_gcs_obj_ref_key.encode("utf-8"))
        gcs_obj_ref = gcs_obj_ref_key.get()
    except:
        logger.error(
            "Could not decode GCSObjectReference key %s", urlsafe_gcs_obj_ref_key
        )
        return abort(404)
    if not isinstance(gcs_obj_ref, GCSObjectReference):
        logger.error(
            "Attempted to access non-GCSObjectReference key %s of type %s",
            gcs_obj_ref_key,
            type(gcs_obj_ref),
        )
        return abort(404)
    else:
        return gcs_obj_ref


def check_access(gcs_obj_ref: GCSObjectReference):
    """Checks that the current user can view the file."""
    if get_current_admin_user() is not None:
        # Allow admin access to all files
        logger.info(
            "Admin %s is viewing GCS Object owned by %s: %s/%s",
            get_current_admin_user().email,
            gcs_obj_ref.key.parent().parent(),
            gcs_obj_ref.bucket_name,
            gcs_obj_ref.object_name,
        )
        return
    elif current_user is None or not current_user.is_authenticated:
        # Anonymous access is not allowed
        logger.error(
            "Anonymous user denied access to GCS Object owned by %s: %s/%s",
            gcs_obj_ref.key.parent().parent(),
            gcs_obj_ref.bucket_name,
            gcs_obj_ref.object_name,
        )
        return abort(401)
    elif current_user.key != gcs_obj_ref.key.parent().parent():
        # Cannot access another user's files
        logger.error(
            "User %s denied access to GCS Object owned by %s: %s/%s",
            current_user.key,
            gcs_obj_ref.key.parent().parent(),
            gcs_obj_ref.bucket_name,
            gcs_obj_ref.object_name,
        )
        return abort(403)
    elif current_user.key == gcs_obj_ref.key.parent().parent():
        # Allow access to user's own files
        return
    else:
        # We should have handled all possible access scenarios.
        return abort(500)


@application_bp.route("/download/f/<string:key>/<string:filename>")
def download_file(key, filename):
    gcs_obj_ref = decode_gcs_obj_ref(key)
    check_access(gcs_obj_ref)

    bucket = gcs.get_bucket(gcs_obj_ref.bucket_name)
    obj = storage.Blob(gcs_obj_ref.object_name, bucket)
    # User can download this object from GCS for 24 hours
    signed_url = generate_signed_url_for(
        obj,
        expiration=datetime.datetime.now(tz=Eastern) + datetime.timedelta(hours=24),
        method="GET",
        version="v4",
        scheme="https",
    )
    return redirect(signed_url)
