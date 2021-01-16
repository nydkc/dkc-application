import logging
import urllib.parse
import json
from flask import abort, request
from flask_login import current_user, login_required
from werkzeug.datastructures import FileStorage
from google.cloud import exceptions, ndb, storage
from common.jinja_functions import toFileInfo, byteConversion
from common.models import Settings
from .models import GCSObjectReference
from . import application_bp

gcs = storage.Client()

MAX_ADVOCACY_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024
MAX_NEWSLETTER_UPLOAD_SIZE_BYTES = 25 * 1024 * 1024


@application_bp.route("/upload/activities/advocacy", methods=["GET", "POST"])
@login_required
def upload_activities_advocacy():
    if request.method == "GET":
        return get_upload_link(request.url)
    else:
        return handle_activities_advocacy_post()


def get_upload_link(redirect_uri):
    # Historical reasons required the frontend to request an upload link for
    # direct uploads to Blobstore. This is now replaced by the AppEngine app
    # proxying the bytes to GCS.
    return redirect_uri


def handle_activities_advocacy_post():
    applicant = current_user
    application = applicant.application.get()

    if application.submit_time:
        logging.info(
            "Attempt to upload advocacy material by %s after submission",
            applicant.email,
        )
        return abort(
            400,
            description="Cannot upload materials for an already submitted application.",
        )

    if len(application.advocacy_materials) >= 5:
        return abort(400, description="Cannot upload more than 5 advocacy materials.")

    new_gcs_obj_ref_key = handle_upload_file(
        application, MAX_ADVOCACY_UPLOAD_SIZE_BYTES
    )
    if not application.advocacy_materials:
        application.advocacy_materials = []
    application.advocacy_materials.append(new_gcs_obj_ref_key)
    application.put()

    return json.dumps(toFileInfo([new_gcs_obj_ref_key]))


def handle_upload_file(application, max_size_bytes):
    upload_files = request.files.getlist("upload_file")
    if len(upload_files) == 0:
        abort(400, description="No files were found in your request")
    elif len(upload_files) > 1:
        abort(400, description="Only one file can be uploaded at a time")
    # We only accept one file upload at a time
    upload_file = upload_files[0]

    settings = ndb.Key(Settings, "config").get()
    bucket = gcs.get_bucket(settings.gcs_bucket)
    key = GCSObjectReference.allocate_ids(parent=application.key, size=1)[0]
    obj_name = "uploads/{}/{}.{}".format(
        settings.due_date.strftime("%Y"),
        key.urlsafe().decode("utf-8"),
        upload_file.filename,
    )
    obj = storage.Blob(obj_name, bucket)
    try:
        obj.upload_from_file(upload_file.stream, content_type=upload_file.content_type)
    except exceptions.GoogleCloudError as e:
        logging.error(
            "Encountered an error while uploading file from %s to GCS: %s",
            current_user.email,
            obj.id,
        )
        return abort(500)
    obj.reload()
    if obj.size > max_size_bytes:
        obj.delete()
        abort(
            413,
            description="File '{}' is too large. Its size of {} is over the limit of {}".format(
                upload_file.filename,
                byteConversion(obj.size),
                byteConversion(max_size_bytes),
            ),
        )
    obj_ref = GCSObjectReference(
        key=key,
        bucket_name=bucket.name,
        object_name=obj.name,
        filename=upload_file.filename,
        content_type=obj.content_type,
        bytes_size=obj.size,
    )
    obj_ref_key = obj_ref.put()
    return obj_ref_key


# class ApplicationUploadHandler(BaseHandler, blobstore_handlers.BlobstoreUploadHandler):

#     def get(self):
#         upload_url = blobstore.create_upload_url('/application/upload')
#         self.response.write(upload_url)

#     @user_required
#     def post(self):
#         applicant = self.user
#         application_key = applicant.application
#         application = application_key.get()

#         if application.submit_time != None:
#             logging.info('Attempt to upload file to submitted application by %s', applicant.email)
#             self.abort(423)
#             return

#         if len(application.other_materials) >= 3:
#             self.abort(403)
#             return

#         upload_files = self.get_uploads('other-material')
#         if len(application.other_materials) + len(upload_files) > 3:
#             for stopped_upload_file in upload_files[5-len(application.advocacy_materials):]:
#                 stopped_upload_file.delete()
#             upload_files = upload_files[0: 3-len(application.other_materials)]

#         for blob_info in upload_files:
#             application.other_materials.append(blob_info.key())
#         application.put()

#         response = []
#         for blob_info in upload_files:
#             response.append('{"key": "%s", "filename": "%s", "content_type": "%s", "size": "%s"}' % (blob_info.key(), blob_info.filename, blob_info.content_type, byteConversion(blob_info.size)))
#         self.response.headers['Content-Type'] = 'application/json'
#         self.response.write(json.dumps(response))

# class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):

#     def get(self, resource):
#         resource = str(urllib.unquote(resource))
#         blob_info = blobstore.BlobInfo.get(resource)
#         if blob_info is None:
#             self.abort(404)
#             return

#         if "image" in blob_info.content_type:
#             image_url = images.get_serving_url(resource) + "=s0"
#             self.redirect(image_url)
#         else:
#             self.send_blob(blob_info)

# class DeleteHandler(BaseHandler):

#     @user_required
#     def get(self, resource):
#         resource = str(urllib.unquote(resource))
#         blob_info = blobstore.BlobInfo.get(resource)
#         if blob_info is None:
#             self.abort(404)
#             return

#         applicant = self.user
#         application_key = applicant.application
#         application = application_key.get()

#         if resource in application.other_materials:
#             application.other_materials.remove(resource)
#         elif resource in application.advocacy_materials:
#             application.advocacy_materials.remove(resource)
#             self.redirect('/application/activities')
#         # Users should not know about files that are not part of their application
#         else:
#             self.abort(404)
#             return
#         application.put()
#         deleted = DeletedFile(parent=self.user.key, user=self.user.key, blob=blob_info.key())
#         deleted.put()

#         self.response.write("Delete Successful: %s" % resource)
