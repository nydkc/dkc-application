from flask import render_template, request
from google.cloud import ndb
from common.models import Settings
from manage.admin_auth.login_manager import admin_login_required, get_current_admin_user
from . import query_helpers
from . import admin_bp


@admin_bp.route("/show/<string:email>", methods=["GET", "POST"])
@admin_login_required
def show(email):
    settings = ndb.Key(Settings, "config").get()
    applicant, application = query_helpers.find_applicant_and_application_by_email(email)
    template_values = {
        "email": email,
        "applicant_id": applicant.key.id(),
        "applicant": applicant,
        "application": application,
        "admin_url": "/admin/show/{}".format(email),
        "settings": settings,
        "current_admin_user": get_current_admin_user(),
    }
    if applicant is None or application is None:
        return render_template("admin/show-404.html", **template_values), 404

    if request.method == "POST":
        return handle_post(applicant, application)
    else:
        return render_template("admin/show.html", **template_values)


def handle_post(appliant, application):
    if request.form.get("notes"):
        application.notes = request.form.get("notes")
        application.put()
    elif request.form.get("graded"):
        print(request.form.get("graded"))
        application.graded = request.form.get("graded") == "on"
        application.put()
    return "ok"
