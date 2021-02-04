import logging
import datetime
from flask import abort, redirect
from google.cloud import ndb, storage
from common.gcs import gcs, generate_signed_url_for
from common.timezone import Eastern
from .models import GCSObjectReference
from . import application_bp


@application_bp.route("/download/f/<string:key>/<string:filename>")
def download_file(key, filename):
    try:
        gcs_obj_ref = ndb.Key(urlsafe=key.encode("utf-8")).get()
    except:
        logging.error("Could not decode key %s with filename: %s", key, filename)
        return abort(404)
    if not isinstance(gcs_obj_ref, GCSObjectReference):
        logging.error(
            "Attempted to access non-GCSObjectReference key %s of type %s",
            key,
            type(gcs_obj_ref),
        )
        return abort(404)

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
