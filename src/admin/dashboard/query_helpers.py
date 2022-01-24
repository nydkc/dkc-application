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
    # Create a lookup to match applicants to the respective application.
    # This is a workaround, since a read-only transaction only allows for ancestor queries.
    lookup = {a.key: a for a in all_applications}
    all_applications = [lookup.get(a.application) for a in all_applicants]
    return all_applicants, all_applications


def get_all_search():
    def _get_unsorted():
        # Use the same projection query as overview to avoid creating another composite index.
        applicants_query = User.query(
            projection=[User.email, User.first_name, User.last_name, User.application]
        )
        applications_query = Application.query(
            projection=[
                Application.grade,
                Application.address,
                Application.city,
                Application.zip_code,
                Application.phone_number,
                Application.division,
                Application.ltg,
                Application.school,
                Application.school_address,
                Application.school_city,
                Application.school_zip_code,
                Application.club_president,
                Application.club_president_phone_number,
                Application.faculty_advisor,
                Application.faculty_advisor_phone_number,
            ]
        )
        return applicants_query.fetch(), applications_query.fetch()

    all_applicants, all_applications = _get_unsorted()
    # Create a lookup to match applicants to the respective application.
    # This is a workaround, since a read-only transaction only allows for ancestor queries.
    lookup = {a.key: a for a in all_applications}
    all_applications = [lookup.get(a.application) for a in all_applicants]
    return all_applicants, all_applications


def get_all_with_emails_submit_time():
    def _get_unsorted():
        # Use the same projection query as overview to avoid creating another composite index.
        applicants_query = User.query(
            projection=[User.email, User.first_name, User.last_name, User.application]
        )
        applications_query = Application.query(projection=[Application.submit_time])
        return applicants_query.fetch(), applications_query.fetch()

    all_applicants, all_applications = _get_unsorted()
    # Create a lookup to match applicants to the respective application.
    # This is a workaround, since a read-only transaction only allows for ancestor queries.
    lookup = {a.key: a for a in all_applications}
    all_applications = [lookup.get(a.application) for a in all_applicants]
    return all_applicants, all_applications


def run_gql(querystring):
    gql_query = ndb.gql(querystring)
    return gql_query.fetch()
