import logging

from flask import after_this_request, redirect, render_template, request, url_for
from flask_login import current_user, login_user
from flask_wtf import FlaskForm, Recaptcha, RecaptchaField
from wtforms import PasswordField, HiddenField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired
from . import auth_bp
from .login_manager import anonymous_only
from .models import User

logger = logging.getLogger(__name__)


class LoginForm(FlaskForm):
    email = EmailField("email", [InputRequired("Email cannot be blank.")])
    password = PasswordField("password", [InputRequired("Password cannot be blank.")])
    recaptcha = RecaptchaField(
        validators=[Recaptcha(message="reCAPTCHA must be solved.")]
    )
    custom_errors = HiddenField("custom_errors")


def should_recaptcha(form):
    attempts_cookie = request.cookies.get("attempts")
    try:
        num_attempts = int(attempts_cookie)
    except (TypeError, ValueError):
        num_attempts = 1

    @after_this_request
    def update_attempts_cookie(resp):
        if current_user.is_authenticated:
            resp.delete_cookie("attempts")
        else:
            # Only increment the number of attempts upon form submission
            resp.set_cookie(
                "attempts",
                str(num_attempts + int(form.is_submitted())),
                max_age=3600,
                httponly=True,
            )
        return resp

    return num_attempts > 5


@auth_bp.route("/login", methods=["GET", "POST"])
@anonymous_only
def login():
    form = LoginForm()
    if not should_recaptcha(form):
        del form.recaptcha
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.get_authenticated_user(email, password)
        if user is not None:
            login_user(user, remember=True)
            return redirect(url_for("application.overview"))
        else:
            logger.warning("Login failed for email: %s", email)
            # Add login failure message and fall-through to template rendering
            form.custom_errors.errors.append(
                "Email and password combination does not correspond to a valid user."
            )

    is_new_account = request.args.get("new") == "1"
    is_password_changed = request.args.get("changed") == "1"

    template_values = {
        "form": form,
        "is_new_account": is_new_account,
        "is_password_changed": is_password_changed,
    }
    return render_template("auth/login.html", **template_values)
