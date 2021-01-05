from flask import render_template
from google.cloud import ndb
from . import application_bp

# class ApplicationVerification(BaseHandler):

#     @user_required
#     def get(self):
#         self._serve_page()

#     @user_required
#     def post(self):
#         applicant = self.user
#         application_key = ndb.Key(urlsafe=self.request.get('form-key'))
#         application = application_key.get()

#         if self._no_verify() or application.submit_time:
#             logging.info("Attempt to modify verification by %s", applicant.email)
#             self._serve_page()
#             return

#         task = self.request.get('task')
#         if task != 'applicant':
#             user_id = self.user.get_id()
#             token = self.user_model.create_signup_token(user_id)
#             verification_url = self.uri_for('verification', type='v', user_id=user_id, signup_token=token, _full=True)
#             logging.info(verification_url)

#             config = ndb.Key(Settings, 'config').get()
#             sg = SendGridClient(config.sendgrid_username, config.sendgrid_password, secure=True)

#             verification_email = Mail(from_name="NYDKC Awards Committee",
#                                       from_email="recognition@nydkc.org",
#                                       subject="Distinguished Key Clubber Application Verification for %s %s" % (applicant.first_name, applicant.last_name)
#             )

#             verifier = ""
#             if task == 'ltg':
#                 application.verification_ltg_email = self.request.get('ltg-email')
#                 application.verification_ltg_token = token
#                 application.verification_ltg_sent = True
#                 verification_email.add_to(application.verification_ltg_email)
#                 verifier = "Lieutenant Governor " + applicant.ltg.title()
#             elif task == 'club-president':
#                 application.verification_club_president_email = self.request.get('club-president-email')
#                 application.verification_club_president_token = token
#                 application.verification_club_president_sent = True
#                 verification_email.add_to(application.verification_club_president_email)
#                 verifier = "Club President " + applicant.club_president.title()
#             elif task == 'faculty-advisor':
#                 application.verification_faculty_advisor_email = self.request.get('faculty-advisor-email')
#                 application.verification_faculty_advisor_token = token
#                 application.verification_faculty_advisor_sent = True
#                 verification_email.add_to(application.verification_faculty_advisor_email)
#                 verifier = "Faculty Advisor " + applicant.faculty_advisor.title()

#             template_values = {
#                 'applicant': applicant,
#                 'verification_url': verification_url,
#                 'verifier': verifier
#             }
#             verification_email.set_html(JINJA_ENVIRONMENT.get_template('verification-email.html').render(template_values))
#             htmlhandler = html2text.HTML2Text()
#             verification_email.set_text(htmlhandler.handle(verification_email.html).encode("UTF+8"))
#             verification_email.add_unique_arg('user_id', str(user_id))

#             code, response = sg.send(verification_email)
#             response = json.loads(response)
#             if response["message"] == "error":
#                 logging.error(("Problem with sending email to %s: " % verification_email.to) + str(response["errors"]))
#                 self._serve_page()
#                 return
#         else:
#             application.verification_applicant = True
#             application.verification_applicant_date = datetime.now()

#         application.put()
#         self._serve_page()

#     def _serve_page(self):
#         template_values = {
#             'application_url': '/application/verification',
#             'no_verify': self._no_verify()
#         }
#         self.render_application('application-verification.html', template_values)

#     def _no_verify(self):
#         applicant = self.user
#         no_verify = (applicant.first_name == '' or applicant.first_name == None)\
#                 or (applicant.last_name == '' or applicant.last_name == None)\
#                 or (applicant.school == '' or applicant.school == None)\
#                 or (applicant.division == '' or applicant.division == None)\
#                 or (applicant.ltg == '' or applicant.ltg == None)\
#                 or (applicant.club_president == '' or applicant.club_president == None)\
#                 or (applicant.club_president_phone_number == '' or applicant.club_president_phone_number == None)\
#                 or (applicant.faculty_advisor == '' or applicant.faculty_advisor == None)\
#                 or (applicant.faculty_advisor_phone_number == '' or applicant.faculty_advisor_phone_number == None)
#         return no_verify


@application_bp.route("/verification", methods=["GET", "POST"])
def verification():
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
    return render_template("application/verification.html", **template_values)
