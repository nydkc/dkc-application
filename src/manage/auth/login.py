import json
import logging
import os
from flask import abort, flash, redirect, request, session, url_for
from common.iam import get_project_iam_policy
from .authlib_oauth import g_oauth
from . import auth_bp

ADMIN_ROLES = ["roles/owner", "roles/editor", "roles/viewer", "roles/browser"]


@auth_bp.route("/login")
def login():
    return g_oauth.google.authorize_redirect(url_for(".oauth2callback", _external=True))


@auth_bp.route("/login/callback")
def oauth2callback():
    token = g_oauth.google.authorize_access_token()
    resp = g_oauth.google.get("https://www.googleapis.com/oauth2/v3/userinfo")
    profile = resp.json()
    email = profile["email"]
    if is_project_admin(email):
        logging.info("User logged in to admin route: %s", email)
        session["admin_credentials"] = token
        session["admin_profile"] = profile
        return redirect(url_for("manage.index.index"))
    else:
        logging.warning("Denied access to non-admin user: %s", email)
        flash(
            "{} is not authorized to view this page.".format(email),
            category="error",
        )
        return redirect(url_for("manage.index.index"))


def is_project_admin(email):
    iam_policy = get_project_iam_policy()
    logging.debug("Current project IAM policy: %s", iam_policy)
    member = "user:{}".format(email)
    for binding in iam_policy["bindings"]:
        # Check if the given email is bound to any of the admin roles
        if binding["role"] in ADMIN_ROLES and member in binding["members"]:
            return True
    return False


@auth_bp.route("/login/testing_is_project_admin")
def test_is_admin():
    # Only expose this route if we are testing locally
    if os.getenv("GAE_ENV", "").startswith("standard"):
        return abort(404)
    email = request.args.get("email")
    return "Is '{}' an admin? Answer is: {}".format(email, is_project_admin(email))
