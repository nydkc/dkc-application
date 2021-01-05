from flask import render_template
from google.cloud import ndb
from . import application_bp

# class ApplicationActivities(BaseHandler):

#     @user_required
#     def get(self):
#         self._serve_page()

#     @user_required
#     def post(self):
#         application_key = ndb.Key(urlsafe=self.request.get('form-key'))
#         application = application_key.get()

#         if application.submit_time:
#             logging.info("Attempt to modify profile by %s", applicant.email)
#             self._serve_page()
#             return

#         if len(self.request.get_all('kiwanis-one-day-event')) > 0:
#             application.kiwanis_one_day = GeneralProject(event=self.request.get('kiwanis-one-day-event'), location=self.request.get('kiwanis-one-day-location'), description=self.request.get('kiwanis-one-day-description'))
#         else:
#             application.kiwanis_one_day = None

#         k_family_projects_events = self.request.get_all('k-family-projects-event')
#         k_family_projects_locations = self.request.get_all('k-family-projects-location')
#         k_family_projects_descriptions = self.request.get_all('k-family-projects-description')
#         application.k_family_projects = []
#         for i in range(0, len(k_family_projects_events)):
#             application.k_family_projects.append(GeneralProject(event=k_family_projects_events[i], location=k_family_projects_locations[i], description=k_family_projects_descriptions[i]))

#         interclub_projects_events = self.request.get_all('interclub-projects-event')
#         interclub_projects_locations = self.request.get_all('interclub-projects-location')
#         interclub_projects_descriptions = self.request.get_all('interclub-projects-description')
#         application.interclub_projects = []
#         for i in range(0, len(interclub_projects_events)):
#             application.interclub_projects.append(GeneralProject(event=interclub_projects_events[i], location=interclub_projects_locations[i], description=interclub_projects_descriptions[i]))

#         application.advocacy_cause = self.request.get('advocacy-cause')
#         application.advocacy_description = self.request.get('advocacy-description')

#         application.committee = self.request.get('committee')
#         application.committee_type = self.request.get('committee-type')
#         application.committee_description = self.request.get('committee-description')

#         application.divisional_newsletter = self.request.get('divisional-newsletter') == 'on'
#         if application.divisional_newsletter:
#             application.divisional_newsletter_info = self.request.get('divisional-newsletter-info')
#         application.district_newsletter = self.request.get('district-newsletter') == 'on'
#         if application.district_newsletter:
#             application.district_newsletter_info = self.request.get('district-newsletter-info')
#         application.district_website = self.request.get('district-website') == 'on'
#         if application.district_website:
#             application.district_website_info = self.request.get('district-website-info')

#         other_projects_events = self.request.get_all('other-projects-event')
#         other_projects_locations = self.request.get_all('other-projects-location')
#         other_projects_descriptions = self.request.get_all('other-projects-description')
#         application.other_projects = []
#         for i in range(0, len(other_projects_events)):
#             application.other_projects.append(GeneralProject(event=other_projects_events[i], location=other_projects_locations[i], description=other_projects_descriptions[i]))

#         application.put()
#         self._serve_page()

#     def _serve_page(self):
#         template_values = {
#             'application_url': '/application/activities',
#         }
#         self.render_application('application-activities.html', template_values)


@application_bp.route("/activities", methods=["GET", "POST"])
def activites():
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
    return render_template("application/activities.html", **template_values)
