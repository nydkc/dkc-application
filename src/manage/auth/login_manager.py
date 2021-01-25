# Note that we don't use flask-login in manage/ for admin users to avoid any
# overlap with that of the DKC application users

import logging
from flask import abort, session
from common.iam import get_project_iam_policy
from .authlib_oauth import refresh_oauth_token
from .models import AdminUser

ADMIN_ROLES = ["roles/owner", "roles/editor", "roles/viewer", "roles/browser"]


def login_admin_user(admin_user: AdminUser):
    admin_user.put()
    session["admin_user"] = admin_user.get_auth_id()


def get_admin_user():
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
            return abort(403)


def logout_admin_user():
    if "admin_user" not in session:
        return None
    user = AdminUser.get_by_auth_id(session["admin_user"])
    user.key.delete()
    del session["admin_user"]


def is_project_admin(email):
    iam_policy = get_project_iam_policy()
    logging.debug("Current project IAM policy: %s", iam_policy)
    member = "user:{}".format(email)
    for binding in iam_policy["bindings"]:
        # Check if the given email is bound to any of the admin roles
        if binding["role"] in ADMIN_ROLES and member in binding["members"]:
            return True
    return False
