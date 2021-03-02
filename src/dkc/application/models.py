from google.cloud import ndb
from common.models import Settings
from dkc.auth.models import AuthToken

# NOTE: Fields with StringProperty are indexed and can be filtered/directly
# queried using projections. Fields with TextProperty are not indexed.


class InternationalProject(ndb.Model):
    section = ndb.TextProperty()
    event = ndb.TextProperty()
    description = ndb.TextProperty()


class DistrictProject(ndb.Model):
    event = ndb.TextProperty()
    charity = ndb.TextProperty()
    description = ndb.TextProperty()


class Divisional(ndb.Model):
    date = ndb.TextProperty()
    location = ndb.TextProperty()


class GeneralProject(ndb.Model):
    event = ndb.TextProperty()
    location = ndb.TextProperty()
    description = ndb.TextProperty()


class GCSObjectReference(ndb.Model):
    bucket_name = ndb.StringProperty()
    object_name = ndb.StringProperty()
    filename = ndb.StringProperty()
    content_type = ndb.StringProperty()
    bytes_size = ndb.IntegerProperty()


class Application(ndb.Model):
    start_time = ndb.DateTimeProperty(auto_now_add=True)
    updated_time = ndb.DateTimeProperty(auto_now=True)
    submit_time = ndb.DateTimeProperty()

    # Profile
    grade = ndb.StringProperty()
    address = ndb.StringProperty()
    city = ndb.StringProperty()
    zip_code = ndb.StringProperty()
    phone_number = ndb.StringProperty()
    division = ndb.StringProperty()
    ltg = ndb.StringProperty()
    school = ndb.StringProperty()
    school_address = ndb.StringProperty()
    school_city = ndb.StringProperty()
    school_zip_code = ndb.StringProperty()
    club_president = ndb.StringProperty()
    club_president_phone_number = ndb.StringProperty()
    faculty_advisor = ndb.StringProperty()
    faculty_advisor_phone_number = ndb.StringProperty()

    # Personal Statement
    personal_statement_choice = ndb.StringProperty()
    personal_statement = ndb.TextProperty()

    # Projects
    international_projects = ndb.StructuredProperty(InternationalProject, repeated=True)
    district_projects = ndb.StructuredProperty(DistrictProject, repeated=True)
    divisionals = ndb.StructuredProperty(Divisional, repeated=True)
    division_projects = ndb.StructuredProperty(GeneralProject, repeated=True)

    # Involvement
    key_club_week_mon = ndb.TextProperty()
    key_club_week_tue = ndb.TextProperty()
    key_club_week_wed = ndb.TextProperty()
    key_club_week_thu = ndb.TextProperty()
    key_club_week_fri = ndb.TextProperty()
    attendance_dtc = ndb.BooleanProperty()
    attendance_fall_rally = ndb.BooleanProperty()
    attendance_kamp_kiwanis = ndb.BooleanProperty()
    attendance_key_leader = ndb.BooleanProperty()
    attendance_ltc = ndb.BooleanProperty()
    attendance_icon = ndb.BooleanProperty()
    positions = ndb.TextProperty()

    # Activities
    kiwanis_one_day = ndb.StructuredProperty(GeneralProject)
    k_family_projects = ndb.StructuredProperty(GeneralProject, repeated=True)
    interclub_projects = ndb.StructuredProperty(GeneralProject, repeated=True)
    advocacy_cause = ndb.TextProperty()
    advocacy_description = ndb.TextProperty()
    advocacy_materials = ndb.KeyProperty(GCSObjectReference, repeated=True)
    committee = ndb.TextProperty()
    committee_type = ndb.TextProperty()
    committee_description = ndb.TextProperty()
    divisional_newsletter = ndb.BooleanProperty()
    divisional_newsletter_info = ndb.TextProperty()
    district_newsletter = ndb.BooleanProperty()
    district_newsletter_info = ndb.TextProperty()
    district_website = ndb.BooleanProperty()
    district_website_info = ndb.TextProperty()
    newsletter_materials = ndb.KeyProperty(GCSObjectReference, repeated=True)
    other_projects = ndb.StructuredProperty(GeneralProject, repeated=True)

    # Other
    recommender_points = ndb.TextProperty()
    outstanding_awards = ndb.StringProperty()  # indexed, for Admin overview
    scoring_reason_two = ndb.TextProperty()
    scoring_reason_three = ndb.TextProperty()
    scoring_reason_four = ndb.TextProperty()
    other_materials = ndb.KeyProperty(GCSObjectReference, repeated=True)

    # Verification
    verification_ltg = ndb.BooleanProperty()
    verification_ltg_email = ndb.StringProperty()
    verification_ltg_sent = ndb.BooleanProperty()
    verification_ltg_token = ndb.KeyProperty(AuthToken)

    verification_club_president = ndb.BooleanProperty()
    verification_club_president_email = ndb.StringProperty()
    verification_club_president_sent = ndb.BooleanProperty()
    verification_club_president_token = ndb.KeyProperty(AuthToken)

    verification_faculty_advisor = ndb.BooleanProperty()
    verification_faculty_advisor_email = ndb.StringProperty()
    verification_faculty_advisor_sent = ndb.BooleanProperty()
    verification_faculty_advisor_token = ndb.KeyProperty(AuthToken)

    verification_applicant = ndb.BooleanProperty()
    verification_applicant_date = ndb.DateTimeProperty()

    # INTERNAL ADMIN USE ONLY
    notes = ndb.TextProperty(default="")
    graded = ndb.BooleanProperty()
