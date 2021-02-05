from google.cloud import ndb
from dkc.auth.models import User
from dkc.application.models import Application


def find_applicant_and_application_by_email(email):
    user = User.find_by_email(email)
    if not user:
        return None, None
    applicant = user
    application = applicant.application.get()
    return applicant, application


def get_all_overview():
    applicants_query = User.query()
    all_applicants = [a for a in applicants_query.fetch()]
    application_keys = [a.application for a in all_applicants]
    all_applications = ndb.get_multi(application_keys)
    return all_applicants, all_applications


def get_all_search():
    applicants_query = User.query().order(User.email)
    all_applicants = [a for a in applicants_query.fetch()]
    application_keys = [a.application for a in all_applicants]
    all_applications = ndb.get_multi(application_keys)
    return all_applicants, all_applications


def get_all_lists():
    applicants_query = User.query().order(User.email)
    all_applicants = [a for a in applicants_query.fetch()]
    application_keys = [a.application for a in all_applicants]
    all_applications = ndb.get_multi(application_keys)
    return all_applicants, all_applications


def run_gql(querystring):
    gql_query = ndb.gql(querystring)
    return gql_query.fetch()
