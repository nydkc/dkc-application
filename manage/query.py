import urllib
from google.appengine.ext import ndb
from manage import *
from dkc.models import *

def get_application_by_email(email):
    applicant = User.get_by_auth_id(email)
    application = applicant.application.get()
    return applicant, application

def get_all_applicants():
    applicants = memcache.get('all_applicants')
    if not applicants:
        query = User.query().order(User.division, User.first_name, User.last_name)
        applicants = query.fetch()
        memcache.add(key='all_applicants', value=applicants, time=600)
    return applicants

def get_all_applications(applicants=None):
    applications = memcache.get('all_applications')
    if not applications:
        if applicants == None:
            applicants = get_all_applicants()
        applications_keys = [a.application for a in applicants]
        applications = ndb.get_multi(applications_keys)
        memcache.add(key='all_applications', value=applications, time=600)
    return applications

def get_all_applicants_applications_no_cache():
    applicants_query = User.query().order(User.division, User.first_name, User.last_name)
    applicants = applicants_query.fetch()
    applications_keys = [a.application for a in applicants]
    applications = ndb.get_multi(applications_keys)
    return applicants, applications

class OverviewApplication():
    def __init__(self, submit_time, early_submission, outstanding_awards):
        self.submit_time = submit_time
        self.early_submission = early_submission
        self.outstanding_awards = outstanding_awards

def get_all_overview():
    applicants = memcache.get('overview_applicants')
    applications = memcache.get('overview_applications')
    if not applicants or not applications:
        applicants_query = User.query().order(User.division, User.first_name, User.last_name)
        applicants = applicants_query.fetch()
        memcache.add(key='overview_applicants', value=applicants, time=600)
        application_keys = [a.application for a in applicants]
        applications = ndb.get_multi(application_keys)
        applications_filtered = [OverviewApplication(a.submit_time, a.early_submission, a.outstanding_awards) for a in applications]
        memcache.add(key='overview_applications', value=applications_filtered, time=600)
    return applicants, applications

def run_gql(querystring):
    query = ndb.gql(querystring)
    return query.fetch()

def get_deleted_files():
    query = DeletedFile.query()
    return query.fetch()
