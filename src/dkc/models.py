import time
from datetime import datetime
from google.appengine.ext import ndb
import webapp2_extras.appengine.auth.models
from webapp2_extras import security
from constants import *
from manage.models import Settings

class SurveyResponse(ndb.Expando):
    timestamp = ndb.DateTimeProperty(auto_now_add=True)

class DeletedFile(ndb.Model):
    user = ndb.KeyProperty()
    blob = ndb.BlobKeyProperty()

class User(webapp2_extras.appengine.auth.models.User):

    def set_password(self, raw_password):
        self.pw = raw_password
        self.put()
        self.password = security.generate_password_hash(raw_password, length=12)

    @classmethod
    def get_by_auth_token(cls, user_id, token, subject='auth'):
        token_key = cls.token_model.get_key(user_id, subject, token)
        user_key = ndb.Key(cls, user_id)
        valid_token, user = ndb.get_multi([token_key, user_key])
        if valid_token and user:
            timestamp = int(time.mktime(valid_token.created.timetuple()))
            return user, timestamp
        return None, None

    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    pw = ndb.StringProperty(indexed=False)
    application = ndb.KeyProperty()

    grade = ndb.StringProperty()
    address = ndb.StringProperty(indexed=False)
    city = ndb.StringProperty(indexed=False)
    zip_code = ndb.StringProperty(indexed=False)
    phone_number = ndb.StringProperty(indexed=False)
    division = ndb.StringProperty()
    ltg = ndb.StringProperty(indexed=False)

    school = ndb.StringProperty(indexed=False)
    school_address = ndb.StringProperty(indexed=False)
    school_city = ndb.StringProperty(indexed=False)
    school_zip_code = ndb.StringProperty(indexed=False)
    club_president = ndb.StringProperty(indexed=False)
    club_president_phone_number = ndb.StringProperty(indexed=False)
    faculty_advisor = ndb.StringProperty(indexed=False)
    faculty_advisor_phone_number = ndb.StringProperty(indexed=False)

class InternationalProject(ndb.Model):
    section = ndb.StringProperty(indexed=False)
    event = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty()

class DistrictProject(ndb.Model):
    event = ndb.StringProperty(indexed=False)
    charity = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty()

class Divisional(ndb.Model):
    date = ndb.StringProperty(indexed=False)
    location = ndb.StringProperty(indexed=False)

class GeneralProject(ndb.Model):
    event = ndb.StringProperty(indexed=False)
    location = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty()

class Application(ndb.Model):
    start_time = ndb.DateTimeProperty(auto_now_add=True)
    updated_time = ndb.DateTimeProperty(auto_now=True)
    submit_time = ndb.DateTimeProperty()
    def is_early(self):
        config = ndb.Key(Settings, 'config').get()
        early_due_date = config.early_due_date
        if self.submit_time:
            return self.submit_time < early_due_date
        else:
            return False

    other_materials = ndb.BlobKeyProperty(repeated=True, indexed=False)

    personal_statement_choice = ndb.StringProperty(indexed=False)
    personal_statement = ndb.TextProperty()

    international_projects = ndb.StructuredProperty(InternationalProject, repeated=True, indexed=False)
    district_projects = ndb.StructuredProperty(DistrictProject, repeated=True, indexed=False)
    divisionals = ndb.StructuredProperty(Divisional, repeated=True, indexed=False)
    division_projects = ndb.StructuredProperty(GeneralProject, repeated=True, indexed=False)
    
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

    kiwanis_one_day = ndb.StructuredProperty(GeneralProject, indexed=False)
    k_family_projects = ndb.StructuredProperty(GeneralProject, repeated=True, indexed=False) 
    interclub_projects = ndb.StructuredProperty(GeneralProject, repeated=True, indexed=False) 
    advocacy_cause = ndb.StringProperty(indexed=False)
    advocacy_description = ndb.TextProperty()
    advocacy_materials = ndb.BlobKeyProperty(repeated=True)
    committee = ndb.StringProperty(indexed=False)
    committee_type = ndb.StringProperty(indexed=False)
    committee_description = ndb.TextProperty()
    divisional_newsletter = ndb.BooleanProperty()
    divisional_newsletter_info = ndb.TextProperty()
    district_newsletter = ndb.BooleanProperty()
    district_newsletter_info = ndb.TextProperty()
    district_website = ndb.BooleanProperty()
    district_website_info = ndb.TextProperty()
    other_projects = ndb.StructuredProperty(GeneralProject, repeated=True, indexed=False)

    early_submission = ndb.ComputedProperty(lambda self: self.is_early())
    early_submission_points = ndb.StringProperty(indexed=False)
    recommender_points = ndb.StringProperty(indexed=False)
    outstanding_awards = ndb.StringProperty()
    
    scoring_reason_two = ndb.TextProperty()
    scoring_reason_three = ndb.TextProperty()
    scoring_reason_four = ndb.TextProperty()

    verification_ltg = ndb.BooleanProperty(default=False)
    verification_ltg_token = ndb.StringProperty(indexed=False, default=None)
    verification_ltg_email = ndb.StringProperty()
    verification_ltg_sent = ndb.BooleanProperty(indexed=False, default=False)

    verification_club_president = ndb.BooleanProperty(default=False)
    verification_club_president_token = ndb.StringProperty(indexed=False, default=None)
    verification_club_president_email = ndb.StringProperty()
    verification_club_president_sent = ndb.BooleanProperty(indexed=False, default=False)

    verification_faculty_advisor = ndb.BooleanProperty(default=False)
    verification_faculty_advisor_token = ndb.StringProperty(indexed=False, default=None)
    verification_faculty_advisor_email = ndb.StringProperty()
    verification_faculty_advisor_sent = ndb.BooleanProperty(indexed=False, default=False)

    verification_applicant = ndb.BooleanProperty(default=False)
    verification_applicant_date = ndb.DateTimeProperty()

    notes = ndb.TextProperty(default="")
    graded = ndb.BooleanProperty()
