import time
from google.appengine.ext import ndb
import webapp2_extras.appengine.auth.models
from webapp2_extras import security
from constants import *

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
    pw = ndb.StringProperty()
    application = ndb.KeyProperty()

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

class InternationalProject(ndb.Model):
    section = ndb.StringProperty()
    event = ndb.StringProperty()
    description = ndb.TextProperty()

class DistrictProject(ndb.Model):
    event = ndb.StringProperty()
    charity = ndb.StringProperty()
    description = ndb.TextProperty()

class Divisional(ndb.Model):
    date = ndb.DateTimeProperty()
    location = ndb.StringProperty()

class GeneralProject(ndb.Model):
    event = ndb.StringProperty()
    location = ndb.StringProperty()
    description = ndb.StringProperty()

class Application(ndb.Model):

    submit_time = ndb.DateTimeProperty()
    def is_early(self):
        due_date = time.strptime(APPLICATION_DUE_DATE, "%b %d %Y")
        return self.submit_time < due_date

    personal_statement = ndb.TextProperty()

    international_projects = ndb.StructuredProperty(InternationalProject, repeated=True)
    district_projects = ndb.StructuredProperty(DistrictProject, repeated=True)
    divisionals = ndb.StructuredProperty(Divisional, repeated=True)
    divison_projects = ndb.StructuredProperty(GeneralProject, repeated=True) 
    
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

    kiwanis_one_day = ndb.TextProperty()
    k_family_projects = ndb.StructuredProperty(GeneralProject, repeated=True) 
    interclub_events = ndb.StructuredProperty(GeneralProject, repeated=True) 
    advocacy_cause = ndb.StringProperty()
    advocacy_description = ndb.TextProperty()
    advocacy_materials = ndb.BlobKeyProperty(repeated=True)
    committee = ndb.StringProperty()
    committee_description = ndb.TextProperty()
    divisional_newsletter = ndb.BooleanProperty()
    divisional_newsletter_info = ndb.TextProperty()
    district_newsletter = ndb.BooleanProperty()
    district_newsletter_info = ndb.TextProperty()
    district_website = ndb.BooleanProperty()
    district_website_info = ndb.TextProperty()
    other_projects = ndb.StructuredProperty(GeneralProject, repeated=True)

    early_submission = ndb.ComputedProperty(lambda self: self.is_early())
    early_submission_points = ndb.StringProperty()
    recommendation = ndb.GenericProperty()
    recommender_points = ndb.StringProperty()
    
    scoring_reason_two = ndb.TextProperty()
    scoring_reason_three = ndb.TextProperty()
    scoring_reason_four = ndb.TextProperty()

    verification_ltg = ndb.BooleanProperty(default=False)
    verification_club_president = ndb.BooleanProperty(default=False)
    verification_faculty_advisor = ndb.BooleanProperty(default=False)
    verification_applicant = ndb.BooleanProperty(default=False)
