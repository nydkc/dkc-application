import json
import logging
import os
from flask import abort, flash, redirect, request, url_for
from .authlib_oauth import g_oauth
from .login_manager import get_current_admin_user, login_admin_user, is_project_admin
from .models import AdminUser, OAuth2Token
from . import auth_bp


@auth_bp.route("/login")
def login():
    if get_current_admin_user():
        return redirect(url_for("manage.admin.overview"))
    return g_oauth.google.authorize_redirect(url_for(".oauth2callback", _external=True))


@auth_bp.route("/login/google_oauth2callback")
def oauth2callback():
    token = g_oauth.google.authorize_access_token()
    profile = g_oauth.google.get(
        "https://openidconnect.googleapis.com/v1/userinfo"
    ).json()
    email = profile["email"]
    if is_project_admin(email):
        logging.info("User logged in to admin route: %s", email)
        # Everytime an admin user goes through the OAuth2 flow, we store their refresh tokens
        admin_user = AdminUser(
            email=profile["email"],
            picture_url=profile["picture"],
            oauth2_token=OAuth2Token(
                provider="google",
                token_type=token["token_type"],
                access_token=token["access_token"],
                refresh_token=token["refresh_token"],
                expires_at=token["expires_at"],
            ),
        )
        login_admin_user(admin_user)
        return redirect(url_for("manage.admin.overview"))
    else:
        logging.warning("Denied access to non-admin user: %s", email)
        flash(
            "{} is not authorized to view this page.".format(email),
            category="error",
        )
        return redirect(url_for("manage.index.index"))


@auth_bp.route("/login/testing_is_project_admin")
def test_is_admin():
    # Only expose this route if we are testing locally
    if os.getenv("GAE_ENV", "").startswith("standard"):
        return abort(404)
    email = request.args.get("email")
    return "Is '{}' an admin? Answer is: {}".format(email, is_project_admin(email))
