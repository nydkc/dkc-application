from flask import render_template
from google.cloud import ndb
from common.models import Settings
from admin.auth.login_manager import admin_login_required, get_current_admin_user
from . import query_helpers
from . import dashboard_bp


@dashboard_bp.route("/overview")
@admin_login_required
def overview():
    settings = Settings.get_config()
    all_applicants, all_applications = query_helpers.get_all_overview()
    template_values = {
        "all_applicants": all_applicants,
        "all_applications": all_applications,
        "admin_url": "/admin/overview",
        "settings": settings,
        "current_admin_user": get_current_admin_user(),
    }
    return render_template("admin_dashboard/overview.html", **template_values)
