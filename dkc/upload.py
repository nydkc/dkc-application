import urllib, json, logging
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images
from dkc import *
from jinja_functions import byteConversion

class ApplicationActivitiesUploadHandler(BaseHandler, blobstore_handlers.BlobstoreUploadHandler):

    def get(self):
        upload_url = blobstore.create_upload_url('/application/activities/upload')
        self.response.write(upload_url)

    @user_required
    def post(self):
        applicant = self.user
        application_key = applicant.application
        application = application_key.get()

        if application.submit_time != None:
            logging.info('Attempt to upload advocacy material to submitted application by %s', applicant.email)
            self.response.write('<script language="javascript" type="text/javascript">window.top.window.finishUpload(0);</script>')
            return

        if len(application.advocacy_materials) >= 5:
            self.response.write('<script language="javascript" type="text/javascript">window.top.window.finishUpload(1);</script>')
            return

        upload_files = self.get_uploads('advocacy-material')
        if len(application.advocacy_materials) + len(upload_files) > 5:
            for stopped_upload_file in upload_files[5-len(application.advocacy_materials):]:
                stopped_upload_file.delete()
            upload_files = upload_files[0: 5-len(application.advocacy_materials)]

        try:
            for blob_info in upload_files:
                application.advocacy_materials.append(blob_info.key())
            application.put()

            self.response.write('<script language="javascript" type="text/javascript">window.top.window.finishUpload(')
            response = []
            for blob_info in upload_files:
                response.append('{"key": "%s", "filename": "%s", "content_type": "%s", "size": "%s"}' % (blob_info.key(), blob_info.filename, blob_info.content_type, byteConversion(blob_info.size)))
            self.response.write(json.dumps(response))
            self.response.write(');</script>')
        except Exception, e:
            logging.error("Error with uploading: %s" % e)
            self.response.clear()
            self.response.write('<script language="javascript" type="text/javascript">window.top.window.finishUpload(0);</script>')

class ApplicationUploadHandler(BaseHandler, blobstore_handlers.BlobstoreUploadHandler):

    def get(self):
        upload_url = blobstore.create_upload_url('/application/upload')
        self.response.write(upload_url)

    @user_required
    def post(self):
        applicant = self.user
        application_key = applicant.application
        application = application_key.get()

        if application.submit_time != None:
            logging.info('Attempt to upload file to submitted application by %s', applicant.email)
            self.abort(423)
            return

        if len(application.other_materials) >= 3:
            self.abort(403)
            return

        upload_files = self.get_uploads('other-material')
        if len(application.other_materials) + len(upload_files) > 3:
            for stopped_upload_file in upload_files[5-len(application.advocacy_materials):]:
                stopped_upload_file.delete()
            upload_files = upload_files[0: 3-len(application.other_materials)]

        for blob_info in upload_files:
            application.other_materials.append(blob_info.key())
        application.put()

        response = []
        for blob_info in upload_files:
            response.append('{"key": "%s", "filename": "%s", "content_type": "%s", "size": "%s"}' % (blob_info.key(), blob_info.filename, blob_info.content_type, byteConversion(blob_info.size)))
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(response))

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):

    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        if blob_info == None:
            self.abort(404)
        else:
            if "image" in blob_info.content_type:
                image_url = images.get_serving_url(resource) + "=s0"
                self.redirect(image_url)
            else:
                self.send_blob(blob_info)

class DeleteHandler(BaseHandler):

    @user_required
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)

        applicant = self.user
        application_key = applicant.application
        application = application_key.get()

        if resource in application.other_materials:
            application.other_materials.remove(resource)
        elif resource in application.advocacy_materials:
            application.advocacy_materials.remove(resource)
            self.redirect('/application/activities')
        application.put()
        deleted = DeletedFile(user=self.user.key, blob=blob_info.key())
        deleted.put()

        self.response.write("Delete Successful: %s" % resource)
