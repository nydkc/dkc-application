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

        application.personal_statement = self.request.get('personal-statement')
        application.put()

class ApplicationProjects(BaseHandler):

    @user_required
    def get(self):
        applicant = self.user
        application_key = applicant.application
        application = application_key.get()

        template_values = {
            'applicant' :applicant,
            'application': application,
            'form_key': application_key.urlsafe(),
            'application_url': '/application/projects'
        }
        self.render_template('application-projects.html', template_values)

    def post(self):
        application_key = ndb.Key(urlsafe=self.request.get('form-key'))
        application = application_key.get()

        international_project_sections = self.request.get_all('international-projects-section')
        international_project_events = self.request.get_all('international-projects-event')
        international_project_descriptions = self.request.get_all('international-projects-description')
        i = 0
        while i < len(application.international_projects):
            application.international_projects[i].section = international_project_sections[i]
            application.international_projects[i].event = international_project_events[i]
            application.international_projects[i].description = international_project_descriptions[i]
            i += 1
        while i < len(international_project_sections):
            application.international_projects.append(InternationalProject(section=international_project_sections[i], event=international_project_events[i], description=international_project_descriptions[i]))
            i += 1

        district_project_events = self.request.get_all('district-projects-event')
        district_project_charities = self.request.get_all('district-projects-charity')
        district_project_descriptions = self.request.get_all('district-projects-description')
        i = 0
        while i < len(application.district_projects):
            application.district_projects[i].event = district_project_events[i]
            application.district_projects[i].charity = district_project_charities[i]
            application.district_projects[i].description = district_project_descriptions[i]
            i += 1
        while i < len(district_project_events):
            application.district_projects.append(DistrictProject(event=district_project_events[i], charity=district_project_charities[i], description=district_project_descriptions[i]))
            i += 1

        divisional_dates = self.request.get_all('divisional-meeting-date')
        divisional_locations = self.request.get_all('divisional-meeting-location')
        i = 0
        while i < len(application.divisionals):
            application.divisionals[i].date = divisional_dates[i]
            application.divisionals[i].location = divisional_locations[i]
            i += 1
        while i < len(divisional_dates):
            application.divisionals.append(Divisional(date=divisional_dates[i], location=divisional_locations[i]))
            i += 1

        division_project_events = self.request.get_all('division-projects-event')
        division_project_locations = self.request.get_all('division-projects-location')
        division_project_descriptions = self.request.get_all('division-projects-description')
        i = 0
        while i < len(application.division_projects):
            application.division_projects[i].event = division_project_events[i]
            application.division_projects[i].location = division_project_locations[i]
            application.division_projects[i].description = division_project_descriptions[i]
            i += 1
        while i< len(division_project_events):
            application.division_projects.append(GeneralProject(event=division_project_events[i], location=division_project_locations[i], description=division_project_descriptions[i]))
            i += 1

        application.put()
