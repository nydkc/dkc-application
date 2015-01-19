import urllib
from google.appengine.ext import ndb
from manage import *
from dkc.models import User

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

def run_gql(querystring):
    query = ndb.gql(querystring)
    return query.fetch()
