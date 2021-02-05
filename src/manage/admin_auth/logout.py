from flask import redirect, url_for
from .login_manager import logout_admin_user
from . import auth_bp


@auth_bp.route("/logout")
def logout():
    logout_admin_user()
    return redirect(url_for("manage.admin_main_page.index"))
