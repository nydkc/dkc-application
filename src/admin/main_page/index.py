from flask import render_template, url_for
from . import main_page_bp


@main_page_bp.route("/")
def index():
    template_values = {
        "login_url": url_for("admin.auth.login"),
    }
    return render_template("admin_main_page/index.html", **template_values)
