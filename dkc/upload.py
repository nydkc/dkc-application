import urllib, json
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images
from dkc import *
from jinja_functions import byteConversion

class ApplicationActivitiesUploadHandler(BaseHandler, blobstore_handlers.BlobstoreUploadHandler):

    def get(self):
        upload_url = blobstore.create_upload_url('/application/activities/upload')
        self.response.write(upload_url)

    def post(self):
        applicant = self.user
        application_key = applicant.application
        application = application_key.get()

        try:
            upload_files = self.get_uploads('advocacy-material')
            for blob_info in upload_files:
                application.advocacy_materials.append(blob_info.key())
            application.put()

            self.response.write('<script language="javascript" type="text/javascript">window.top.window.finishUpload(')
            self.response.write('[')
            for blob_info in upload_files:
                self.response.write('\'{"url": "/serve/%s/%s", "filename": "%s", "content_type": "%s", "size": "%s"}\', ' % (blob_info.key(), blob_info.filename, blob_info.filename, blob_info.content_type, byteConversion(blob_info.size)))
            self.response.write(']')
            self.response.write(');</script>')
        except Exception, e:
            print "Error with uploading: %s" % e
            self.response.clear()
            self.response.write('<script language="javascript" type="text/javascript">window.top.window.finishUpload(0);</script>')

class ApplicationUploadHandler(BaseHandler, blobstore_handlers.BlobstoreUploadHandler):

    def get(self):
        upload_url = blobstore.create_upload_url('/application/upload')
        self.response.write(upload_url)

    def post(self):
        applicant = self.user
        application_key = applicant.application
        application = application_key.get()

        upload_files = self.get_uploads('other-material')
        for blob_info in upload_files:
            application.other_materials.append(blob_info.key())
        application.put()

        response = []
        for blob_info in upload_files:
            response.append('{"url": "/serve/%s/%s", "filename": "%s", "content_type": "%s", "size": "%s"}' % (blob_info.key(), blob_info.filename, blob_info.filename, blob_info.content_type, byteConversion(blob_info.size)))
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(response))

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):

    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        if "image" in blob_info.content_type:
            image_url = images.get_serving_url(resource) + "=s0"
            self.redirect(image_url)
        else:
            self.send_blob(blob_info)
