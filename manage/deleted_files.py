from google.appengine.ext import ndb, blobstore
from manage import *
import query

class DeletedFilesHandler(AdminBaseHandler):

    def get(self):
        deleted_files = query.get_deleted_files()
        deleted_files_keys = [deleted_file.key.urlsafe() for deleted_file in deleted_files]
        template_values = {
            'deleted_files': deleted_files,
            'deleted_files_keys': deleted_files_keys
        }
        self.render_template('admin-deleted_files.html', template_values);

class DeleteDeletedFilesHandler(AdminBaseHandler):

    def post(self, deleted_file_key):
        deleted_file_key = ndb.Key(urlsafe=deleted_file_key)
        deleted_file = deleted_file_key.get()
        blobstore.delete(deleted_file.blob)
        deleted_file_key.delete()
        self.response.write("Successfully deleted: %s" % deleted_file_key)
