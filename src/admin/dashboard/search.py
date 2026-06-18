import time
from flask import render_template, request
from google.cloud import ndb
from common.models import Settings
from admin.auth.login_manager import admin_login_required, get_current_admin_user
from . import query_helpers
from . import dashboard_bp


@dashboard_bp.route("/search")
@admin_login_required
def search():
    settings = Settings.get_config()

    start_time = time.time()
    querystring = request.args.get("q") or ""
    results = handle_search(querystring)
    time_elapsed = time.time() - start_time

    template_values = {
        "q": querystring,
        "query_results": results,
        "time_elapsed": time_elapsed,
        "admin_url": "/admin/search",
        "settings": settings,
        "current_admin_user": get_current_admin_user(),
    }
    return render_template("admin_dashboard/search.html", **template_values)


def handle_search(querystring):
    if not querystring:
        return None

    all_applicants, all_applications = query_helpers.get_all_search()
    matched_results = [
        (applicant, application)
        for applicant, application in zip(all_applicants, all_applications)
        if applicant_matches(applicant, application, querystring)
    ]
    return matched_results


def applicant_matches(applicant, application, querystring):
    """
    Checks whether the given `querystring` is contained in the profile fields
    in `applicant` and `application`.

    The caller must ensure that if `applicant` and `application` are entities
    returned from a projection query, that the projection contains the profile
    fields that are searched.
    """
    if applicant is None or application is None:
        return False
    search_fields = [
        applicant.first_name,
        applicant.last_name,
        applicant.email,
        application.grade,
        application.address,
        application.city,
        application.zip_code,
        application.phone_number,
        application.division,
        application.ltg,
        application.school,
        application.school_address,
        application.school_city,
        application.school_zip_code,
        application.club_president,
        application.club_president_phone_number,
        application.faculty_advisor,
        application.faculty_advisor_phone_number,
    ]
    return any(map(lambda f: querystring.lower() in str(f).lower(), search_fields))
