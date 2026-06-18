from flask import abort
from . import dummy_bp


@dummy_bp.route("/error")
def error():
    return abort(400, description="dummy error")
