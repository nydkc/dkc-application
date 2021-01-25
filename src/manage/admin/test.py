from . import admin_bp
import json
from manage.auth.login_manager import get_admin_user


@admin_bp.route("/test")
def test():
    return get_admin_user().email
