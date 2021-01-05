from flask import render_template
from google.cloud import ndb
from . import application_bp

# class ApplicationInvolvement(BaseHandler):

#     @user_required
#     def get(self):
#         self._serve_page()

#     @user_required
#     def post(self):
#         application_key = ndb.Key(urlsafe=self.request.get('form-key'))
#         application = application_key.get()

#         if application.submit_time:
#             logging.info("Attempt to modify involvement by %s", applicant.email)
#             self._serve_page()
#             return

#         application.key_club_week_mon = self.request.get('key-club-week-monday')
#         application.key_club_week_tue = self.request.get('key-club-week-tuesday')
#         application.key_club_week_wed = self.request.get('key-club-week-wednesday')
#         application.key_club_week_thu = self.request.get('key-club-week-thursday')
#         application.key_club_week_fri = self.request.get('key-club-week-friday')

#         application.attendance_dtc = self.request.get('attendance-dtc') == 'on'
#         application.attendance_fall_rally = self.request.get('attendance-fall-rally') == 'on'
#         application.attendance_kamp_kiwanis = self.request.get('attendance-kamp-kiwanis') == 'on'
#         application.attendance_key_leader = self.request.get('attendance-key-leader') == 'on'
#         application.attendance_ltc = self.request.get('attendance-ltc') == 'on'
#         application.attendance_icon = self.request.get('attendance-icon') == 'on'

#         application.positions = self.request.get('positions')

#         application.put()
#         self._serve_page()

#     def _serve_page(self):
#         config = ndb.Key(Settings, 'config').get()
#         template_values = {
#             'application_url': '/application/involvement',
#             'config': config
#         }
#         self.render_application('application-involvement.html', template_values)


@application_bp.route("/involvement", methods=["GET", "POST"])
def involvement():
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
    return render_template("application/involvement.html", **template_values)
