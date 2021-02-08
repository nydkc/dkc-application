import logging
from flask import abort, make_response
from flask_login import current_user, login_required
from google.api_core import exceptions as api_exceptions
from google.cloud import exceptions, ndb, storage
from common.gcs import gcs
from .models import GCSObjectReference
from . import application_bp


@ndb.transactional()
def remove_file_from_application(application_key, gcs_obj_ref_key):
    application = application_key.get()
    for materials in (
        application.advocacy_materials,
        application.newsletter_materials,
        application.other_materials,
    ):
        if gcs_obj_ref_key in materials:
            materials.remove(gcs_obj_ref_key)
    application.put()
    gcs_obj_ref_key.delete()


def delete_referenced_gcs_object(gcs_obj_ref: GCSObjectReference):
    bucket = gcs.get_bucket(gcs_obj_ref.bucket_name)
    obj = storage.Blob(gcs_obj_ref.object_name, bucket)
    try:
        obj.delete()
    except (exceptions.NotFound, api_exceptions.NotFound) as e:
        logging.error("Could not find file in GCS to delete: %s", obj.name)


@application_bp.route("/delete/f/<string:key>", methods=["POST"])
@login_required
def delete_file(key):
    try:
        gcs_obj_ref = ndb.Key(urlsafe=key.encode("utf-8")).get()
    except:
        logging.error("Could not decode key %s", key)
        abort(400, description="Invalid key")
    if not isinstance(gcs_obj_ref, GCSObjectReference):
        logging.error(
            "Attempted to delete non-GCSObjectReference key %s of type %s",
            key,
            type(gcs_obj_ref),
        )
        abort(400, description="Invalid key")
    # Users should not know about files that don't belong to them
    applicant = current_user
    if applicant.application != gcs_obj_ref.key.parent():
        logging.error(
            "Attempted to delete file that doesn't belong to %s", applicant.email
        )
        abort(403)

    delete_referenced_gcs_object(gcs_obj_ref)
    remove_file_from_application(applicant.application, gcs_obj_ref.key)

    return make_response(("", 204))
