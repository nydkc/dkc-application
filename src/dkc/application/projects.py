from flask import render_template
from google.cloud import ndb
from . import application_bp

# class ApplicationProjects(BaseHandler):

#     @user_required
#     def get(self):
#         self._serve_page()

#     @user_required
#     def post(self):
#         application_key = ndb.Key(urlsafe=self.request.get('form-key'))
#         application = application_key.get()

#         if application.submit_time:
#             logging.info("Attempt to modify projects by %s", applicant.email)
#             self._serve_page()
#             return

#         international_project_sections = self.request.get_all('international-projects-section')
#         international_project_events = self.request.get_all('international-projects-event')
#         international_project_descriptions = self.request.get_all('international-projects-description')
#         application.international_projects = []
#         for i in range(0, len(international_project_sections)):
#             application.international_projects.append(InternationalProject(section=international_project_sections[i], event=international_project_events[i], description=international_project_descriptions[i]))

#         district_project_events = self.request.get_all('district-projects-event')
#         district_project_charities = self.request.get_all('district-projects-charity')
#         district_project_descriptions = self.request.get_all('district-projects-description')
#         application.district_projects = []
#         for i in range(0, len(district_project_events)):
#             application.district_projects.append(DistrictProject(event=district_project_events[i], charity=district_project_charities[i], description=district_project_descriptions[i]))

#         divisional_dates = self.request.get_all('divisional-meeting-date')
#         divisional_locations = self.request.get_all('divisional-meeting-location')
#         application.divisionals = []
#         for i in range(0, len(divisional_dates)):
#             application.divisionals.append(Divisional(date=divisional_dates[i], location=divisional_locations[i]))

#         division_project_events = self.request.get_all('division-projects-event')
#         division_project_locations = self.request.get_all('division-projects-location')
#         division_project_descriptions = self.request.get_all('division-projects-description')
#         application.division_projects = []
#         for i in range(0, len(division_project_events)):
#             application.division_projects.append(GeneralProject(event=division_project_events[i], location=division_project_locations[i], description=division_project_descriptions[i]))

#         application.put()
#         self._serve_page()

#     def _serve_page(self):
#         template_values = {
#             'application_url': '/application/projects'
#         }
#         self.render_application('application-projects.html', template_values)


@application_bp.route("/projects", methods=["GET", "POST"])
def projects():
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
    return render_template("application/projects.html", **template_values)
