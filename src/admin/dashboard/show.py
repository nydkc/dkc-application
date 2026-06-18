from flask import render_template, request
from google.cloud import ndb
from common.models import Settings
from admin.auth.login_manager import admin_login_required, get_current_admin_user
from . import query_helpers
from . import dashboard_bp


@dashboard_bp.route("/show/<string:email>", methods=["GET", "POST"])
@admin_login_required
def show(email):
    settings = Settings.get_config()
    applicant, application = query_helpers.find_applicant_and_application_by_email(
        email
    )

    # Handle 404 before accessing attributes
    if applicant is None or application is None:
        template_values = {
            "email": email,
            "settings": settings,
            "current_admin_user": get_current_admin_user(),
            "admin_url": f"/admin/show/{email}",
        }
        return render_template("admin_dashboard/show-404.html", **template_values), 404

    template_values = {
        "email": email,
        "applicant_id": applicant.key.id(),
        "applicant": applicant,
        "application": application,
        "admin_url": f"/admin/show/{email}",
        "settings": settings,
        "current_admin_user": get_current_admin_user(),
    }

    if request.method == "POST":
        return handle_post(applicant, application)
    else:
        return render_template("admin_dashboard/show.html", **template_values)


def handle_post(appliant, application):
    if request.form.get("notes"):
        application.notes = request.form.get("notes")
        application.put()
    elif request.form.get("graded"):
        print(request.form.get("graded"))
        application.graded = request.form.get("graded") == "on"
        application.put()
    return "ok"
