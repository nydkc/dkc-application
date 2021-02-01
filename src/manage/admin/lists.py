from flask import render_template
from google.cloud import ndb
from common.models import Settings
from manage.auth.login_manager import admin_login_required, get_current_admin_user
from . import query_helpers
from . import admin_bp

@admin_bp.route("/lists")
@admin_login_required
def lists():
    settings = ndb.Key(Settings, "config").get()
    all_applicants, all_applications = query_helpers.get_all_overview()
    template_values = {
        "all_applicants": all_applicants,
        "all_applications": all_applications,
        "admin_url": "/admin/lists",
        "settings": settings,
        "current_admin_user": get_current_admin_user(),
    }
    return render_template("admin/lists.html", **template_values)
