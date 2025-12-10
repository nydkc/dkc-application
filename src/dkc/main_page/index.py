from flask import render_template
from google.cloud import ndb
from common.models import Settings
from . import main_page_bp


@main_page_bp.route("/")
def index():
    settings = Settings.get_config()
    template_values = {
        "settings": settings,
    }
    return render_template("main_page/index.html", **template_values)
