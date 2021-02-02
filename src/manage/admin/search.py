import time
from flask import render_template, request
from google.cloud import ndb
from common.models import Settings
from manage.auth.login_manager import admin_login_required, get_current_admin_user
from . import query_helpers
from . import admin_bp


@admin_bp.route("/search")
@admin_login_required
def search():
    settings = ndb.Key(Settings, "config").get()

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
    return render_template("admin/search.html", **template_values)


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
