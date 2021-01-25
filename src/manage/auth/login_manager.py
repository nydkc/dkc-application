# Note that we don't use flask-login in manage/ for admin users to avoid any
# overlap with that of the DKC application users

from flask import session
from .models import AdminUser


def login_admin_user(user: AdminUser):
    session["admin_user"] = user.get_auth_id()


def get_admin_user():
    if "admin_user" not in session:
        return None
    return AdminUser.get_by_auth_id(session["admin_user"])
