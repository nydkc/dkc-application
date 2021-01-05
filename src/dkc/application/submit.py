from flask import render_template
from google.cloud import ndb
from . import application_bp

# class ApplicationSubmit(BaseHandler):

#     @user_required
#     def get(self):
#         self._serve_page(self._not_complete())

#     @user_required
#     def post(self):
#         application_key = ndb.Key(urlsafe=self.request.get('form-key'))
#         application = application_key.get()

#         not_complete = self._not_complete()
#         if True in not_complete.values(): # If there is an error
#             self.response.set_status(204)
#             self._serve_page(errors=self._not_complete())
#         else:
#             applicant = self.user
#             application.submit_time = datetime.now()
#             application.put()

#             config = ndb.Key(Settings, 'config').get()
#             sg = SendGridClient(config.sendgrid_username, config.sendgrid_password, secure=True)

#             verification_email = Mail(from_name="NYDKC Awards Committee",
#                                       from_email="recognition@nydkc.org",
#                                       subject="DKC Application Confirmation for %s %s" % (applicant.first_name, applicant.last_name),
#                                       to=applicant.email
#             )

#             template_values = {
#                 'applicant': applicant,
#                 'application': application
#             }
#             verification_email.set_html(JINJA_ENVIRONMENT.get_template('confirmation-email.html').render(template_values))
#             htmlhandler = html2text.HTML2Text()
#             verification_email.set_text(htmlhandler.handle(verification_email.html).encode("UTF+8"))

#             code, response = sg.send(verification_email)
#             response = json.loads(response)
#             if response["message"] == "error":
#                 logging.error(("Problem with sending email to %s: " % verification_email.to) + str(response["errors"]))
#                 self._serve_page()
#                 return

#             self.redirect('/application')

#     def _serve_page(self, errors={'profile':False, 'personal_statement':False, 'projects':False, 'involvement':False, 'activities':False, 'other':False, 'verification':False}):
#         template_values = {
#             'user_id': self.user.get_id(),
#             'application_url': '/application/submit',
#             'profile': errors['profile'],
#             'personal_statement': errors['personal_statement'],
#             'projects': errors['projects'],
#             'involvement': errors['involvement'],
#             'activities': errors['activities'],
#             'other': errors['other'],
#             'verification': errors['verification']
#         }
#         self.render_application('application-submit.html', template_values)

#     def _not_complete(self):
#         applicant = self.user
#         application = applicant.application.get()

#         not_complete_profile = (applicant.first_name == None or applicant.first_name == '')\
#                 or (applicant.last_name == None or applicant.last_name == '')\
#                 or (applicant.school == None or applicant.school == '')\
#                 or (applicant.division == None or applicant.division == '')\
#                 or (applicant.ltg == None or applicant.ltg == '')\
#                 or (applicant.club_president == None or applicant.club_president == '')\
#                 or (applicant.club_president_phone_number == None or applicant.club_president_phone_number == '')\
#                 or (applicant.faculty_advisor == None or applicant.faculty_advisor == '')\
#                 or (applicant.faculty_advisor_phone_number == None or applicant.faculty_advisor_phone_number == '')\

#         not_complete_personal_statement = (application.personal_statement == None or application.personal_statement == '')

#         not_complete_projects = (len(application.international_projects) == 0)\
#                 and (len(application.district_projects) == 0)\
#                 and (len(application.divisionals) == 0)\
#                 and (len(application.division_projects) == 0)\
#                     and (application.scoring_reason_two == None or application.scoring_reason_two == '')

#         not_complete_involvement = (application.key_club_week_mon == None or application.key_club_week_mon == '')\
#                 and (application.key_club_week_tue == None or application.key_club_week_tue == '')\
#                 and (application.key_club_week_wed == None or application.key_club_week_wed == '')\
#                 and (application.key_club_week_thu == None or application.key_club_week_thu == '')\
#                 and (application.key_club_week_fri == None or application.key_club_week_fri == '')\
#                 and (application.attendance_dtc == None)\
#                 and (application.attendance_fall_rally == None)\
#                 and (application.attendance_kamp_kiwanis == None)\
#                 and (application.attendance_key_leader == None)\
#                 and (application.attendance_ltc == None)\
#                 and (application.attendance_icon == None)\
#                 and (application.positions == None or application.positions == '')\
#                     and (application.scoring_reason_three == None or application.scoring_reason_three == '')

#         not_complete_activities = (application.kiwanis_one_day == None)\
#                 and (len(application.k_family_projects) == 0)\
#                 and (len(application.interclub_projects) == 0)\
#                 and (application.advocacy_cause == None or application.advocacy_cause == '')\
#                 and (application.committee == None or application.committee == '')\
#                 and (application.divisional_newsletter == None)\
#                 and (application.district_newsletter == None)\
#                 and (application.district_website == None)\
#                 and (len(application.other_projects) == 0)\
#                     and (application.scoring_reason_four == None or application.scoring_reason_four == '')

#         verification_count = 0
#         if application.verification_ltg:
#             verification_count += 1
#         if application.verification_club_president:
#             verification_count += 1
#         if application.verification_faculty_advisor:
#             verification_count += 1
#         if application.verification_applicant:
#             verification_count += 1
#         not_complete_verification = verification_count < 3 # Need at least 3 of 4 verifications

#         not_complete_other = (not_complete_projects
#                 or not_complete_personal_statement\
#                 or not_complete_involvement\
#                 or not_complete_activities\
#                 or application.outstanding_awards == None or application.outstanding_awards == '')

#         return {'profile': not_complete_profile,
#                 'personal_statement': not_complete_personal_statement,
#                 'projects': not_complete_projects,
#                 'involvement': not_complete_involvement,
#                 'activities': not_complete_activities,
#                 'other': not_complete_other,
#                 'verification': not_complete_verification}


@application_bp.route("/submit", methods=["GET", "POST"])
def submit():
    settings = {
        "due_date": 2020,
    }
    applicant = {}
    application = {}
    template_values = {
        "settings": settings,
        "applicant": applicant,
        "application": application,
    }
    return render_template("application/submit.html", **template_values)
