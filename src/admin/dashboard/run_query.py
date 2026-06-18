import logging
from flask import render_template, request
from google.cloud import ndb
from common.models import Settings
from admin.auth.login_manager import admin_login_required, get_current_admin_user
from . import query_helpers
from . import dashboard_bp

logger = logging.getLogger(__name__)


@dashboard_bp.route("/run_query")
@admin_login_required
def run_query():
    settings = Settings.get_config()

    querystring = request.args.get("q") or ""
    results, error = handle_run_query(querystring)

    template_values = {
        "q": querystring,
        "query_results": results,
        "query_error": error,
        "admin_url": "/admin/run_query",
        "settings": settings,
        "current_admin_user": get_current_admin_user(),
    }
    return render_template("admin_dashboard/run_query.html", **template_values)


def handle_run_query(querystring):
    if not querystring:
        return None, None

    try:
        results = query_helpers.run_gql(querystring)
        error = None
    except Exception as e:
        logger.error("Failed to run query: %s", e)
        results = []
        error = e

    return results, error
