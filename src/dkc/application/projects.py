import logging
from flask import render_template, request
from flask_login import current_user, login_required
from google.cloud import ndb
from common.models import Settings
from .models import DistrictProject, Divisional, GeneralProject, InternationalProject
from . import application_bp

logger = logging.getLogger(__name__)


@application_bp.route("/projects", methods=["GET", "POST"])
@login_required
def projects():
    settings = ndb.Key(Settings, "config").get()
    applicant = current_user
    application = applicant.application.get()

    if request.method == "POST":
        handle_post(applicant, application)

    template_values = {
        "applicant": applicant,
        "application": application,
        "application_url": "/application/projects",
        "settings": settings,
    }
    return render_template("application/projects.html", **template_values)


def handle_post(applicant, application):
    if application.submit_time:
        logger.warning(
            "Attempt to modify projects by %s after submission",
            applicant.email,
        )
        return

    international_project_sections = request.form.getlist(
        "international-projects-section"
    )
    international_project_events = request.form.getlist("international-projects-event")
    international_project_descriptions = request.form.getlist(
        "international-projects-description"
    )
    application.international_projects = []
    for i in range(len(international_project_sections)):
        application.international_projects.append(
            InternationalProject(
                section=international_project_sections[i],
                event=international_project_events[i],
                description=international_project_descriptions[i],
            )
        )

    district_project_events = request.form.getlist("district-projects-event")
    district_project_charities = request.form.getlist("district-projects-charity")
    district_project_descriptions = request.form.getlist(
        "district-projects-description"
    )
    application.district_projects = []
    for i in range(len(district_project_events)):
        application.district_projects.append(
            DistrictProject(
                event=district_project_events[i],
                charity=district_project_charities[i],
                description=district_project_descriptions[i],
            )
        )

    divisional_dates = request.form.getlist("divisional-meeting-date")
    divisional_locations = request.form.getlist("divisional-meeting-location")
    application.divisionals = []
    for i in range(len(divisional_dates)):
        application.divisionals.append(
            Divisional(date=divisional_dates[i], location=divisional_locations[i])
        )

    division_project_events = request.form.getlist("division-projects-event")
    division_project_locations = request.form.getlist("division-projects-location")
    division_project_descriptions = request.form.getlist(
        "division-projects-description"
    )
    application.division_projects = []
    for i in range(len(division_project_events)):
        application.division_projects.append(
            GeneralProject(
                event=division_project_events[i],
                location=division_project_locations[i],
                description=division_project_descriptions[i],
            )
        )

    application.put()
