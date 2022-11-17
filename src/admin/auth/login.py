import logging
import os
from flask import abort, flash, redirect, request, url_for
from .authlib_oauth import g_oauth
from .login_manager import get_current_admin_user, login_admin_user, is_project_admin
from .models import AdminUser, OAuth2Token
from . import auth_bp

logger = logging.getLogger(__name__)


@auth_bp.route("/login")
def login():
    if get_current_admin_user():
        return redirect(url_for("admin_dashboard.overview"))
    return g_oauth.google.authorize_redirect(url_for(".oauth2callback", _external=True))


@auth_bp.route("/login/google_oauth2callback")
def oauth2callback():
    token = g_oauth.google.authorize_access_token()
    profile = g_oauth.google.get(
        "https://openidconnect.googleapis.com/v1/userinfo"
    ).json()
    email = profile["email"]
    if is_project_admin(email):
        logger.info("User logged in to admin route: %s", email)
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
        return redirect(url_for("admin_dashboard.overview"))
    else:
        logger.warning("Denied access to non-admin user: %s", email)
        flash(
            "{} is not authorized to view this page.".format(email),
            category="error",
        )
        return redirect(url_for("admin_main_page.index"))


@auth_bp.route("/login/test_is_project_admin")
def test_is_admin():
    # Only expose this route if we are testing locally
    if os.getenv("GAE_ENV", "").startswith("standard"):
        return abort(404)
    email = request.args.get("email")
    return "Is '{}' an admin? Answer is: {}".format(email, is_project_admin(email))
