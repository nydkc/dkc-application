# Note that we don't use flask-login in manage/ for admin users to avoid any
# overlap with that of the DKC application users

import functools
import logging
from flask import abort, g, redirect, session, url_for
from common.iam import get_project_iam_policy
from .authlib_oauth import refresh_oauth_token
from .models import AdminUser

logger = logging.getLogger(__name__)

ADMIN_ROLES = ["roles/owner", "roles/editor", "roles/viewer", "roles/browser"]


def admin_login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if get_current_admin_user() is None:
            return redirect(url_for("manage.admin_main_page.index"))
        else:
            return f(*args, **kwargs)

    return decorated_function


def login_admin_user(admin_user: AdminUser):
    admin_user.put()
    session["admin_user"] = admin_user.get_auth_id()


def get_current_admin_user() -> AdminUser:
    # Use application context cached value for the admin user
    if "admin_user" in g:
        return g.admin_user
    # Otherwise, retrieve the admin user specified in the session
    if "admin_user" not in session:
        return None
    user = AdminUser.get_by_auth_id(session["admin_user"])
    if user is None:
        return None
    # Ensure that the admin user is still valid by refreshing OAuth2 token
    if user.oauth2_token.requires_refresh():
        refresh_oauth_token(user.oauth2_token)
        # Ensure that the admin user still has permissions on GCP project
        if is_project_admin(user.email):
            user.put()
        else:
            user.key.delete()
            logout_admin_user()
            return None
    g.admin_user = user
    return g.admin_user


def logout_admin_user():
    if "admin_user" not in session:
        return None
    user = AdminUser.get_by_auth_id(session["admin_user"])
    user.key.delete()
    del session["admin_user"]


def is_project_admin(email):
    iam_policy = get_project_iam_policy()
    logger.debug("Current project IAM policy: %s", iam_policy)
    member = "user:{}".format(email)
    for binding in iam_policy["bindings"]:
        # Check if the given email is bound to any of the admin roles
        if binding["role"] in ADMIN_ROLES and member in binding["members"]:
            return True
    return False
