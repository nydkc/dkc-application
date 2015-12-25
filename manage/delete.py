import urllib, logging
from google.appengine.ext import ndb
from webapp2_extras.appengine.auth.models import Unique
from manage import *
from dkc.models import *
import query

class DeleteAccountHandler(AdminBaseHandler):
    """
    Handler to delete applicant accounts along with their associated
    application. This will also remove the unique entry, allowing others to
    use the deleted account's email.
    WARNING: This should be used only to remove spam accounts.
    """

    def post(self):
        emails_to_delete = self.request.get_all('email')
        emails_deleted = []
        applicants_to_delete = []
        applications_to_delete = []
        uniques_to_delete = []
        for email in emails_to_delete:
            applicant, application = query.get_application_by_email(email)
            if applicant:
                applicants_to_delete.append(applicant.key)
                emails_deleted.append(email)
            if application:
                applications_to_delete.append(application.key)
            # Delete auth ids which are just emails
            uniques_to_delete.append('User.auth_id:' + email)
            # Delete unique emails
            uniques_to_delete.append('User.email:' + email)
        ndb.delete_multi(applicants_to_delete + applications_to_delete)
        Unique.delete_multi(uniques_to_delete)
        self.response.write("Deleted:\n")
        self.response.write("\t- %d applicants\n" % len(applicants_to_delete))
        self.response.write("\t- %d applications\n" % len(applications_to_delete))
        self.response.write("\t- %d uniques\n" % len(uniques_to_delete))
        logging.warning("Deleted applicants: %s", ', '.join(emails_deleted))
