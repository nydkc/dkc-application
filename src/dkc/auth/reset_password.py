import json
import logging
import uuid
from flask import abort, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms.validators import EqualTo, Length
from wtforms.widgets import PasswordInput
from google.cloud import ndb
from .login_manager import anonymous_only
from .models import User, AuthToken
from . import auth_bp

logger = logging.getLogger(__name__)


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "password",
        [Length(min=8, message="Your password must be at least 8 characters.")],
        widget=PasswordInput(hide_value=False),
    )
    confirm_password = PasswordField(
        "confirm_password",
        [EqualTo("password", message="Passwords must match.")],
    )


@auth_bp.route("/reset-password/p/<string:token_key>", methods=["GET", "POST"])
@anonymous_only
def reset_password(token_key):
    try:
        token = ndb.Key(urlsafe=token_key.encode("utf-8")).get()
    except:
        logger.error("Could not decode key %s", token_key)
        return abort(400, description="Invalid token")
    if not isinstance(token, AuthToken):
        logger.error(
            "Attempted to access non-AuthToken key %s of type %s",
            token_key,
            type(token),
        )
        return abort(400, description="Invalid token")

    form = ResetPasswordForm()
    user = token.key.parent().get()

    if form.validate_on_submit():
        update_password(user.key, token.key, form.password.data)
        return redirect(url_for(".login", changed="1"))

    template_values = {
        "form": form,
        "email": user.email,
        "password_reset_url": url_for(".reset_password", token_key=token_key),
    }
    return render_template("auth/reset_password.html", **template_values)


@ndb.transactional()
def update_password(user_key, token_key, password):
    auth_credential_id = uuid.uuid4().hex
    user = user_key.get()
    user.password_hash = User.hash_password(password)
    user.auth_credential_id = auth_credential_id
    user.put()
    token_key.delete()
