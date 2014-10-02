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

        application.personal_statement_choice = self.request.get("personal-statement-choice")
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

class ApplicationInvolvement(BaseHandler):

    @user_required
    def get(self):
        applicant = self.user
        application_key = applicant.application
        application = application_key.get()

        template_values = {
            'applicant' :applicant,
            'application': application,
            'form_key': application_key.urlsafe(),
            'application_url': '/application/involvement'
        }
        self.render_template('application-involvement.html', template_values)

    def post(self):
        application_key = ndb.Key(urlsafe=self.request.get('form-key'))
        application = application_key.get()

        application.key_club_week_mon = self.request.get('key-club-week-monday')
        application.key_club_week_tue = self.request.get('key-club-week-tuesday')
        application.key_club_week_wed = self.request.get('key-club-week-wednesday')
        application.key_club_week_thu = self.request.get('key-club-week-thursday')
        application.key_club_week_fri = self.request.get('key-club-week-friday')

        application.attendance_dtc = self.request.get('attendance-dtc') == 'on'
        application.attendance_fall_rally = self.request.get('attendance-fall-rally') == 'on'
        application.attendance_kamp_kiwanis = self.request.get('attendance-kamp-kiwanis') == 'on'
        application.attendance_key_leader = self.request.get('attendance-key-leader') == 'on'
        application.attendance_ltc = self.request.get('attendance-ltc') == 'on'
        application.attendance_icon = self.request.get('attendance-icon') == 'on'

        application.positions = self.request.get('positions')

        application.put()

class ApplicationActivities(BaseHandler):

    @user_required
    def get(self):
        applicant = self.user
        application_key = applicant.application
        application = application_key.get()

        template_values = {
            'applicant' :applicant,
            'application': application,
            'form_key': application_key.urlsafe(),
            'application_url': '/application/activities'
        }
        self.render_template('application-activities.html', template_values)

    def post(self):
        application_key = ndb.Key(urlsafe=self.request.get('form-key'))
        application = application_key.get()

        application.kiwanis_one_day = GeneralProject(event=self.request.get('kiwanis-one-day-event'), location=self.request.get('kiwanis-one-day-location'), description=self.request.get('kiwanis-one-day-description'))

        k_family_projects_events = self.request.get_all('k-family-projects-event')
        k_family_projects_locations = self.request.get_all('k-family-projects-location')
        k_family_projects_descriptions = self.request.get_all('k-family-projects-description')
        i = 0
        while i < len(application.k_family_projects):
            application.k_family_projects[i].event = k_family_projects_events[i]
            application.k_family_projects[i].location = k_family_projects_locations[i]
            application.k_family_projects[i].description = k_family_projects_descriptions[i]
            i += 1
        while i < len(k_family_projects_events):
            application.k_family_projects.append(GeneralProject(event=k_family_projects_events[i], location=k_family_projects_locations[i], description=k_family_projects_descriptions[i]))
            i += 1

        interclub_projects_events = self.request.get_all('interclub-projects-event')
        interclub_projects_locations = self.request.get_all('interclub-projects-location')
        interclub_projects_descriptions = self.request.get_all('interclub-projects-description')
        i = 0
        while i < len(application.interclub_projects):
            application.interclub_projects[i].event = interclub_projects_events[i]
            application.interclub_projects[i].location = interclub_projects_locations[i]
            application.interclub_projects[i].description = interclub_projects_descriptions[i]
            i += 1
        while i < len(interclub_projects_events):
            application.interclub_projects.append(GeneralProject(event=interclub_projects_events[i], location=interclub_projects_locations[i], description=interclub_projects_descriptions[i]))
            i += 1

        application.advocacy_cause = self.request.get('advocacy-cause')
        application.advocacy_description = self.request.get('advocacy-description')

        application.committee = self.request.get('committee')
        application.committee_type = self.request.get('committee-type')
        application.committee_description = self.request.get('committee-description')

        application.divisional_newsletter = self.request.get('divisional-newsletter') == 'on'
        if application.divisional_newsletter:
            application.divisional_newsletter_info = self.request.get('divisional-newsletter-info')
        application.district_newsletter = self.request.get('district-newsletter') == 'on'
        if application.district_newsletter:
            application.district_newsletter_info = self.request.get('district-newsletter-info')
        application.district_website = self.request.get('district-website') == 'on'
        if application.district_website:
            application.district_website_info = self.request.get('district-website-info')

        other_projects_events = self.request.get_all('other-projects-event')
        other_projects_locations = self.request.get_all('other-projects-location')
        other_projects_descriptions = self.request.get_all('other-projects-description')
        i = 0
        while i < len(application.other_projects):
            application.other_projects[i].event = other_projects_events[i]
            application.other_projects[i].location = other_projects_locations[i]
            application.other_projects[i].description = other_projects_descriptions[i]
            i += 1
        while i < len(other_projects_events):
            application.other_projects.append(GeneralProject(event=other_projects_events[i], location=other_projects_locations[i], description=other_projects_descriptions[i]))
            i += 1

        application.put()

class ApplicationScoring(BaseHandler):

    @user_required
    def get(self):
        applicant = self.user
        application_key = applicant.application
        application = application_key.get()

        template_values = {
            'applicant' :applicant,
            'application': application,
            'form_key': application_key.urlsafe(),
            'application_url': '/application/scoring'
        }
        self.render_template('application-scoring.html', template_values)

    def post(self):
        application_key = ndb.Key(urlsafe=self.request.get('form-key'))
        application = application_key.get()

        application.early_submission_points = self.request.get('early-submission-points')
        application.recommender_points = self.request.get('recommender-points')

        application.scoring_reason_two = self.request.get('scoring-reason-two')
        application.scoring_reason_three = self.request.get('scoring-reason-three')
        application.scoring_reason_four = self.request.get('scoring-reason-four')

        application.put()

class ApplicationVerification(BaseHandler):

    @user_required
    def get(self):
        applicant = self.user
        application_key = applicant.application
        application = application_key.get()

        template_values = {
            'applicant' :applicant,
            'application': application,
            'form_key': application_key.urlsafe(),
            'application_url': '/application/verification'
        }
        self.render_template('application-verification.html', template_values)
