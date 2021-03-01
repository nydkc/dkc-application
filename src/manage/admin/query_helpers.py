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
    def _get_unsorted():
        applicants_query = User.query(
            projection=[User.email, User.first_name, User.last_name, User.application]
        )
        applications_query = Application.query(
            projection=[
                Application.submit_time,
                Application.division,
                Application.outstanding_awards,
                Application.graded,
            ]
        )
        return applicants_query.fetch(), applications_query.fetch()

    all_applicants, all_applications = _get_unsorted()
    # Create a lookup to match applicants to the respective application
    # This is a workaround, since a read-only transaction only allows for ancestor queries.
    lookup = {a.key: a for a in all_applications}
    all_applications = [lookup.get(a.application) for a in all_applicants]
    return all_applicants, all_applications


def get_all_search():
    applicants_query = User.query().order(User.email)
    all_applicants = [a for a in applicants_query.fetch()]
    application_keys = [a.application for a in all_applicants]
    all_applications = ndb.get_multi(application_keys)
    return all_applicants, all_applications


def get_all_with_emails_submit_time():
    def _get_unsorted():
        applicants_query = User.query(projection=[User.email, User.application])
        applications_query = Application.query(projection=[Application.submit_time])
        return applicants_query.fetch(), applications_query.fetch()

    all_applicants, all_applications = _get_unsorted()
    # Create a lookup to match applicants to the respective application
    # This is a workaround, since a read-only transaction only allows for ancestor queries.
    lookup = {a.key: a for a in all_applications}
    all_applications = [lookup.get(a.application) for a in all_applicants]
    return all_applicants, all_applications


def run_gql(querystring):
    gql_query = ndb.gql(querystring)
    return gql_query.fetch()
