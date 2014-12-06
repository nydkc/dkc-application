import os, webapp2, jinja2
from datetime import datetime
from google.appengine.ext import ndb, blobstore
from google.appengine.api import mail
from dkc import *
from models import *

class ApplicationOverview(BaseHandler):

    @user_required
    def get(self):
        self._serve_page()

    @user_required
    def post(self):
        self._serve_page()

    def _serve_page(self):
        template_values = {
            'user_id': self.user.get_id(),
            'application_url': '/application/overview'
        }
        self.render_application('application-overview.html', template_values)

class ApplicationProfile(BaseHandler):

    @user_required
    def get(self):
        self._serve_page()

    @user_required
    def post(self):
        applicant = self.user
        application = applicant.application.get()

        if application.submit_time:
            logging.info("Attempt to modify profile by %s", applicant.email)
            self._serve_page()
            return

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
        self._serve_page()

    def _serve_page(self):
        template_values = {
            'application_url': '/application/profile'
        }
        self.render_application('application-profile.html', template_values)

class ApplicationPersonalStatement(BaseHandler):

    @user_required
    def get(self):
        self._serve_page()

    @user_required
    def post(self):
        application_key = ndb.Key(urlsafe=self.request.get('form-key'))
        application = application_key.get()

        if application.submit_time:
            logging.info("Attempt to modify personal statement by %s", applicant.email)
            self._serve_page()
            return

        application.personal_statement_choice = self.request.get("personal-statement-choice")
        application.personal_statement = self.request.get('personal-statement')
        application.put()
        self._serve_page()

    def _serve_page(self):
        template_values = {
            'application_url': '/application/personal-statement'
        }
        self.render_application('application-personal_statement.html', template_values)

class ApplicationProjects(BaseHandler):

    @user_required
    def get(self):
        self._serve_page()

    @user_required
    def post(self):
        application_key = ndb.Key(urlsafe=self.request.get('form-key'))
        application = application_key.get()

        if application.submit_time:
            logging.info("Attempt to modify projects by %s", applicant.email)
            self._serve_page()
            return

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
        self._serve_page()

    def _serve_page(self):
        template_values = {
            'application_url': '/application/projects'
        }
        self.render_application('application-projects.html', template_values)

class ApplicationInvolvement(BaseHandler):

    @user_required
    def get(self):
        self._serve_page()

    @user_required
    def post(self):
        application_key = ndb.Key(urlsafe=self.request.get('form-key'))
        application = application_key.get()

        if application.submit_time:
            logging.info("Attempt to modify involvement by %s", applicant.email)
            self._serve_page()
            return

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
        self._serve_page()

    def _serve_page(self):
        template_values = {
            'application_url': '/application/involvement'
        }
        self.render_application('application-involvement.html', template_values)

class ApplicationActivities(BaseHandler):

    @user_required
    def get(self):
        self._serve_page()

    @user_required
    def post(self):
        application_key = ndb.Key(urlsafe=self.request.get('form-key'))
        application = application_key.get()

        if application.submit_time:
            logging.info("Attempt to modify profile by %s", applicant.email)
            self._serve_page()
            return

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
        self._serve_page()

    def _serve_page(self):
        template_values = {
            'application_url': '/application/activities',
        }
        self.render_application('application-activities.html', template_values)

class ApplicationOther(BaseHandler):

    @user_required
    def get(self):
        self._serve_page()

    @user_required
    def post(self):
        application_key = ndb.Key(urlsafe=self.request.get('form-key'))
        application = application_key.get()

        if application.submit_time:
            logging.info("Attempt to modify scoring by %s", applicant.email)
            self._serve_page()
            return

        if self.request.get('early-submission-checkbox'):
            application.early_submission_points = self.request.get('early-submission-points')
        else:
            application.early_submission_points = "-1"

        if self.request.get('recommender-checkbox'):
            application.recommender_points = self.request.get('recommender-points')
        else:
            application.recommender_points = "-1"

        application.scoring_reason_two = self.request.get('scoring-reason-two')
        application.scoring_reason_three = self.request.get('scoring-reason-three')
        application.scoring_reason_four = self.request.get('scoring-reason-four')

        application.put()
        self._serve_page()

    def _serve_page(self):
        template_values = {
            'application_url': '/application/other'
        }
        self.render_application('application-other.html', template_values)

class ApplicationVerification(BaseHandler):

    @user_required
    def get(self):
        self._serve_page()

    @user_required
    def post(self):
        applicant = self.user
        application_key = ndb.Key(urlsafe=self.request.get('form-key'))
        application = application_key.get()

        if self._no_verify() or application.submit_time:
            logging.info("Attempt to modify verification by %s", applicant.email)
            self._serve_page()
            return

        task = self.request.get('task')
        if task != 'applicant':
            user_id = self.user.get_id()
            token = self.user_model.create_signup_token(user_id)
            verification_url = self.uri_for('verification', type='v', user_id=user_id, signup_token=token, _full=True)
            print verification_url

            verification_email = mail.EmailMessage(sender="NYDKC Awards Committee <verification@dkc-app.appspotmail.com>",
                                                   subject="Distinguished Key Clubber Application Verification for %s %s" % (applicant.first_name, applicant.last_name),
                                                   reply_to="dkc.applications@nydkc.org",
                                                   body="""
You've been requested to verify the application of %s %s

Please click the link below to verify your information on the application. If the information is incorrect, please make sure to email or contact the applicant at <a href="mailto:%s">%s</a> so that he/she can put the correct information onto the application.

In addition to verifying your information, you are also verifying that this applicant is a member in good standing of Key Club International.

Click the following link to verify: <a href="%s">%s</a>

If you have any questions or concerns, feel free to reply to this email and we will try our best to address them!

Yours in spirit and service,
The New York District Awards Committee
                                                   """ % (applicant.first_name, applicant.last_name, applicant.email, applicant.email, verification_url, verification_url),
            )

            verifier = ""
            if task == 'ltg':
                application.verification_ltg_email = self.request.get('ltg-email')
                application.verification_ltg_token = token
                application.verification_ltg_sent = True
                verification_email.to = application.verification_ltg_email
                verifier = "Lieutenant Governor " + applicant.ltg.title()
            elif task == 'club-president':
                application.verification_club_president_email = self.request.get('club-president-email')
                application.verification_club_president_token = token
                application.verification_club_president_sent = True
                verification_email.to = application.verification_club_president_email
                verifier = "Club President " + applicant.club_president.title()
            elif task == 'faculty-advisor':
                application.verification_faculty_advisor_email = self.request.get('faculty-advisor-email')
                application.verification_faculty_advisor_token = token
                application.verification_faculty_advisor_sent = True
                verification_email.to = application.verification_faculty_advisor_email
                verifier = "Faculty Advisor " + applicant.faculty_advisor.title()

            template_values = {
                'applicant': applicant,
                'verification_url': verification_url,
                'verifier': verifier
            }
            verification_email.html = JINJA_ENVIRONMENT.get_template('verification-email.html').render(template_values)
            import html2text
            htmlhandler = html2text.HTML2Text()
            verification_email.body = htmlhandler.handle(verification_email.html).encode("UTF+8")

            verification_email.send()
        else:
            application.verification_applicant = True
            application.verification_applicant_date = datetime.now()

        application.put()
        self._serve_page()

    def _serve_page(self):
        template_values = {
            'application_url': '/application/verification',
            'no_verify': self._no_verify()
        }
        self.render_application('application-verification.html', template_values)

    def _no_verify(self):
        applicant = self.user
        no_verify = (applicant.first_name == '' or applicant.first_name == None)\
                or (applicant.last_name == '' or applicant.last_name == None)\
                or (applicant.school == '' or applicant.school == None)\
                or (applicant.division == '' or applicant.division == None)\
                or (applicant.ltg == '' or applicant.ltg == None)\
                or (applicant.club_president == '' or applicant.club_president == None)\
                or (applicant.club_president_phone_number == '' or applicant.club_president_phone_number == None)\
                or (applicant.faculty_advisor == '' or applicant.faculty_advisor == None)\
                or (applicant.faculty_advisor_phone_number == '' or applicant.faculty_advisor_phone_number == None)
        return no_verify

class ApplicationSubmit(BaseHandler):

    @user_required
    def get(self):
        self._serve_page(self._not_complete())

    @user_required
    def post(self):
        application_key = ndb.Key(urlsafe=self.request.get('form-key'))
        application = application_key.get()

        not_complete = self._not_complete()
        if True in not_complete.values(): # If there is an error
            self.response.set_status(204)
            self._serve_page(errors=self._not_complete())
        else:
            application.submit_time = datetime.now()
            application.put()
            self.redirect('/')

    def _serve_page(self, errors={'profile':False, 'personal_statement':False, 'projects':False, 'involvement':False, 'activities':False, 'other':False, 'verification':False}):
        template_values = {
            'user_id': self.user.get_id(),
            'application_url': '/application/submit',
            'profile': errors['profile'],
            'personal_statement': errors['personal_statement'],
            'projects': errors['projects'],
            'involvement': errors['involvement'],
            'activities': errors['activities'],
            'other': errors['other'],
            'verification': errors['verification']
        }
        self.render_application('application-submit.html', template_values)

    def _not_complete(self):
        applicant = self.user
        application = applicant.application.get()

        not_complete_profile = (applicant.first_name == None or applicant.first_name == '')\
                or (applicant.last_name == None or applicant.last_name == '')\
                or (applicant.school == None or applicant.school == '')\
                or (applicant.division == None or applicant.division == '')\
                or (applicant.ltg == None or applicant.ltg == '')\
                or (applicant.club_president == None or applicant.club_president == '')\
                or (applicant.club_president_phone_number == None or applicant.club_president_phone_number == '')\
                or (applicant.faculty_advisor == None or applicant.faculty_advisor == '')\
                or (applicant.faculty_advisor_phone_number == None or applicant.faculty_advisor_phone_number == '')\

        not_complete_personal_statement = (application.personal_statement == None or application.personal_statement == '')

        not_complete_projects = (len(application.international_projects) == 0)\
                and (len(application.district_projects) == 0)\
                and (len(application.divisionals) == 0)\
                and (len(application.division_projects) == 0)\
                    and (application.scoring_reason_two == None or application.scoring_reason_two == '')

        not_complete_involvement = (application.key_club_week_mon == None or application.key_club_week_mon == '')\
                and (application.key_club_week_tue == None or application.key_club_week_tue == '')\
                and (application.key_club_week_wed == None or application.key_club_week_wed == '')\
                and (application.key_club_week_thu == None or application.key_club_week_thu == '')\
                and (application.key_club_week_fri == None or application.key_club_week_fri == '')\
                and (application.attendance_dtc == None)\
                and (application.attendance_fall_rally == None)\
                and (application.attendance_kamp_kiwanis == None)\
                and (application.attendance_key_leader == None)\
                and (application.attendance_ltc == None)\
                and (application.attendance_icon == None)\
                and (application.positions == None or application.positions == '')\
                    and (application.scoring_reason_three == None or application.scoring_reason_three == '')

        not_complete_activities = (application.kiwanis_one_day == None)\
                and (len(application.k_family_projects) == 0)\
                and (len(application.interclub_projects) == 0)\
                and (application.advocacy_cause == None or application.advocacy_cause == '')\
                and (application.committee == None or application.committee == '')\
                and (application.divisional_newsletter == None)\
                and (application.district_newsletter == None)\
                and (application.district_website == None)\
                and (len(application.other_projects) == 0)\
                    and (application.scoring_reason_four == None or application.scoring_reason_four == '')

        not_complete_verification = not (application.verification_ltg\
                and application.verification_club_president\
                and application.verification_faculty_advisor\
                and application.verification_applicant)

        not_complete_other = (not_complete_projects
                or not_complete_personal_statement\
                or not_complete_involvement\
                or not_complete_activities)

        return {'profile': not_complete_profile,
                'personal_statement': not_complete_personal_statement,
                'projects': not_complete_projects,
                'involvement': not_complete_involvement,
                'activities': not_complete_activities,
                'other': not_complete_other,
                'verification': not_complete_verification}
