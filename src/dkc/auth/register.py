import logging
import uuid
from flask import redirect, render_template, request, url_for
from flask_wtf import FlaskForm, Recaptcha, RecaptchaField
from google.cloud import ndb
from wtforms import PasswordField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, EqualTo, InputRequired, Length
from wtforms.widgets import PasswordInput
from common.models import Settings
from dkc.application.models import Application
from .login_manager import anonymous_only
from .models import User, UniqueUserTracking
from . import auth_bp

logger = logging.getLogger(__name__)


class RegistrationForm(FlaskForm):
    first_name = StringField(
        "first_name", [InputRequired("Your first name cannot be blank.")]
    )
    last_name = StringField(
        "last_name", [InputRequired("Your last name cannot be blank.")]
    )
    email = EmailField("email", [Email("Please enter a valid email address.")])
    password = PasswordField(
        "password",
        [Length(min=8, message="Your password must be at least 8 characters.")],
        widget=PasswordInput(hide_value=False),
    )
    confirm_password = PasswordField(
        "confirm_password",
        [EqualTo("password", message="Passwords must match.")],
    )
    recaptcha = RecaptchaField(
        validators=[Recaptcha(message="reCAPTCHA must be solved.")]
    )


class EmailAlreadyExistsError(Exception):
    pass


@ndb.transactional()
def create_user_application(email: str, password: str, first_name: str, last_name: str):
    auth_credential_id = uuid.uuid4().hex
    new_user = User(
        email=email,
        password_hash=User.hash_password(password),
        first_name=first_name,
        last_name=last_name,
        auth_credential_id=auth_credential_id,
    )
    # Check for email duplication
    if UniqueUserTracking.get_by_id(new_user._get_unique_attributes_id()) is not None:
        raise EmailAlreadyExistsError()
    new_user_key = new_user.put()
    new_application = Application(parent=new_user_key)
    new_application_key = new_application.put()
    # Update user with bidirectional pointer to application
    new_user.application = new_application_key
    new_user.put()
    # Track the newly created user's email to prevent future duplication
    UniqueUserTracking(id=new_user._get_unique_attributes_id()).put()
    return new_user


@auth_bp.route("/register", methods=["GET", "POST"])
@anonymous_only
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        password = form.password.data
        email = form.email.data
        try:
            new_user = create_user_application(email, password, first_name, last_name)
            logger.info(
                "Created new user '%s %s', with email: %s",
                new_user.first_name,
                new_user.last_name,
                new_user.email,
            )
            return redirect(url_for(".login", new=1))
        except EmailAlreadyExistsError:
            # Add email already taken error and fall-through to template rendering
            logger.warning(
                "Attempted to create an account with an existing email: %s", email
            )
            form.email.errors.append(
                "The email '{}' is already taken. Please use a different email.".format(
                    email
                )
            )
    template_values = {
        "form": form,
    }
    return render_template("auth/register.html", **template_values)
