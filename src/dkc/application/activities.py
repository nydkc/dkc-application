import logging
from flask import abort, render_template, request
from flask_login import current_user, login_required
from google.cloud import ndb
from common.models import Settings
from .models import GeneralProject
from . import application_bp

logger = logging.getLogger(__name__)


@application_bp.route("/activities", methods=["GET", "POST"])
@login_required
def activites():
    settings = ndb.Key(Settings, "config").get()
    applicant = current_user
    application = applicant.application.get()

    if request.method == "POST":
        handle_post(applicant, application)

    template_values = {
        "applicant": applicant,
        "application": application,
        "application_url": "/application/activities",
        "settings": settings,
    }
    return render_template("application/activities.html", **template_values)


def handle_post(applicant, application):
    if application.submit_time:
        logger.warning(
            "Attempt to modify activities by %s after submission",
            applicant.email,
        )
        return abort(409)

    application.kiwanis_one_day = None
    if len(request.form.getlist("kiwanis-one-day-event")) > 0:
        application.kiwanis_one_day = GeneralProject(
            event=request.form.get("kiwanis-one-day-event"),
            location=request.form.get("kiwanis-one-day-location"),
            description=request.form.get("kiwanis-one-day-description"),
        )

    k_family_projects_events = request.form.getlist("k-family-projects-event")
    k_family_projects_locations = request.form.getlist("k-family-projects-location")
    k_family_projects_descriptions = request.form.getlist(
        "k-family-projects-description"
    )
    application.k_family_projects = []
    for i in range(len(k_family_projects_events)):
        application.k_family_projects.append(
            GeneralProject(
                event=k_family_projects_events[i],
                location=k_family_projects_locations[i],
                description=k_family_projects_descriptions[i],
            )
        )

    interclub_projects_events = request.form.getlist("interclub-projects-event")
    interclub_projects_locations = request.form.getlist("interclub-projects-location")
    interclub_projects_descriptions = request.form.getlist(
        "interclub-projects-description"
    )
    application.interclub_projects = []
    for i in range(len(interclub_projects_events)):
        application.interclub_projects.append(
            GeneralProject(
                event=interclub_projects_events[i],
                location=interclub_projects_locations[i],
                description=interclub_projects_descriptions[i],
            )
        )

    application.advocacy_cause = request.form.get("advocacy-cause")
    application.advocacy_description = request.form.get("advocacy-description")

    application.committee = request.form.get("committee")
    application.committee_type = request.form.get("committee-type")
    application.committee_description = request.form.get("committee-description")

    application.divisional_newsletter = (
        request.form.get("divisional-newsletter") == "on"
    )
    application.divisional_newsletter_info = None
    if application.divisional_newsletter:
        application.divisional_newsletter_info = request.form.get(
            "divisional-newsletter-info"
        )
    application.district_newsletter = request.form.get("district-newsletter") == "on"
    application.district_newsletter_info = None
    if application.district_newsletter:
        application.district_newsletter_info = request.form.get(
            "district-newsletter-info"
        )
    application.district_website = request.form.get("district-website") == "on"
    application.district_website_info = None
    if application.district_website:
        application.district_website_info = request.form.get("district-website-info")

    other_projects_events = request.form.getlist("other-projects-event")
    other_projects_locations = request.form.getlist("other-projects-location")
    other_projects_descriptions = request.form.getlist("other-projects-description")
    application.other_projects = []
    for i in range(len(other_projects_events)):
        application.other_projects.append(
            GeneralProject(
                event=other_projects_events[i],
                location=other_projects_locations[i],
                description=other_projects_descriptions[i],
            )
        )

    application.put()
