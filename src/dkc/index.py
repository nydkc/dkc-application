from flask import Blueprint, render_template
from google.cloud import ndb
from common.models import Settings

index_bp = Blueprint("index", __name__, template_folder="templates")


@index_bp.route("/")
def index():
    settings = ndb.Key(Settings, "config").get()
    template_values = {"settings": settings}
    return render_template("index.html", **template_values)
