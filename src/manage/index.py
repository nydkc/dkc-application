from flask import Blueprint, render_template, url_for

index_bp = Blueprint("manage.index", __name__, template_folder="templates")


@index_bp.route("/")
def index():
    template_values = {
        "login_url": url_for("manage.auth.login"),
    }
    return render_template("manage/index.html", **template_values)
