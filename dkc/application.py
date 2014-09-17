import os, webapp2, jinja2
from google.appengine.ext import ndb
from dkc import *
from models import *

class ApplicationProfile(BaseHandler):

    @user_required
    def get(self):
        applicant = self.user
        template_values = {
            'applicant': applicant,
            'application_url': '/application/profile'
        }
        self.render_template('application-profile.html', template_values)

    def post(self):
        applicant = self.user
        applicant.first_name = self.request.get('first-name')
        applicant.last_name = self.request.get('last-name')
        applicant.grade = self.request.get('grade')
        applicant.address = self.request.get('address')
        applicant.city = self.request.get('city')
        applicant.zip_code = self.request.get('zip-code')
        applicant.phone_number = self.request.get('phone-number')
        applicant.division = self.request.get('division')
        applicant.ltg = self.request.get('ltg')
        applicant.school = self.request.get('school')
        applicant.school_address = self.request.get('school-address')
        applicant.school_city = self.request.get('school-city')
        applicant.school_zip_code = self.request.get('school-zip-code')
        applicant.club_president = self.request.get('club-president')
        applicant.club_president_phone_number = self.request.get('club-president-phone-number')
        applicant.faculty_advisor = self.request.get('faculty-advisor')
        applicant.faculty_advisor_phone_number = self.request.get('faculty-advisor-phone-number')
        applicant.put()

class ApplicationPersonalStatement(BaseHandler):

    @user_required
    def get(self):
        applicant = self.user
        application_key = applicant.application
        application = application_key.get()
        template_values = {
            'applicant': applicant,
            'application': application,
            'form_key': application_key.urlsafe(),
            'application_url': '/application/personal-statement'
        }
        self.render_template('application-personal_statement.html', template_values)

    def post(self):
        application_key = ndb.Key(urlsafe=self.request.get('form-key'))
        application = application_key.get()
        applicant = application_key.parent().get()

        application.personal_statement = self.request.get('personal-statement')
        application.put()
