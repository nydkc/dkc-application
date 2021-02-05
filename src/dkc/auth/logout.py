from flask import redirect, url_for
from flask_login import logout_user
from . import auth_bp


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main_page.index"))
