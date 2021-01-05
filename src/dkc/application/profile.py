from flask import render_template
from google.cloud import ndb
from . import application_bp

# class ApplicationProfile(BaseHandler):

#     @user_required
#     def get(self):
#         self._serve_page()

#     @user_required
#     def post(self):
#         applicant = self.user
#         application = applicant.application.get()

#         if application.submit_time:
#             logging.info("Attempt to modify profile by %s", applicant.email)
#             self._serve_page()
#             return

#         applicant.first_name = self.request.get('first-name')
#         applicant.last_name = self.request.get('last-name')
#         applicant.grade = self.request.get('grade')
#         applicant.address = self.request.get('address')
#         applicant.city = self.request.get('city')
#         applicant.zip_code = self.request.get('zip-code')
#         applicant.phone_number = self.request.get('phone-number')
#         applicant.division = self.request.get('division')
#         applicant.ltg = self.request.get('ltg')
#         applicant.school = self.request.get('school')
#         applicant.school_address = self.request.get('school-address')
#         applicant.school_city = self.request.get('school-city')
#         applicant.school_zip_code = self.request.get('school-zip-code')
#         applicant.club_president = self.request.get('club-president')
#         applicant.club_president_phone_number = self.request.get('club-president-phone-number')
#         applicant.faculty_advisor = self.request.get('faculty-advisor')
#         applicant.faculty_advisor_phone_number = self.request.get('faculty-advisor-phone-number')
#         applicant.put()
#         self._serve_page()

#     def _serve_page(self):
#         template_values = {
#             'application_url': '/application/profile'
#         }
#         self.render_application('application-profile.html', template_values)

@application_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    settings = {
        "due_date": 2020,
    }
    applicant = {}
    template_values = {
        "settings": settings,
        "applicant": applicant
    }
    return render_template('application/profile.html', **template_values)
