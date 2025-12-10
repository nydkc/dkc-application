import logging
from flask import abort, render_template, url_for
from flask_wtf import FlaskForm, Recaptcha, RecaptchaField
from wtforms.fields import EmailField
from wtforms.validators import Email as EmailValidator
from google.cloud import ndb
from common.models import Settings
from common.email_provider import (
    get_email_provider,
    Email,
    Subject,
    HtmlContent,
    CustomArgs,
)
from .login_manager import anonymous_only
from .models import User, AuthToken
from . import auth_bp

logger = logging.getLogger(__name__)


class ForgetForm(FlaskForm):
    email = EmailField("email", [EmailValidator("Please enter a valid email address.")])
    recaptcha = RecaptchaField(
        validators=[Recaptcha(message="reCAPTCHA must be solved.")]
    )


@auth_bp.route("/forgot", methods=["GET", "POST"])
@anonymous_only
def forgot():
    form = ForgetForm()
    template_values = {
        "form": form,
    }

    if form.validate_on_submit():
        email = form.email.data
        user = User.find_by_email(email)
        if user is None:
            logger.warning("Could not find any user for email: %s", email)
            form.email.errors.append(f"No account found with email '{email}'.")
        else:
            token_key = create_password_reset_auth_token(user)
            send_password_reset_email(user, token_key)
            template_values["forgot_email_sent_to"] = email

    settings = Settings.get_config()
    template_values.update(
        {
            "settings": settings,
        }
    )

    return render_template("auth/forgot.html", **template_values)


def create_password_reset_auth_token(user):
    key = AuthToken.allocate_ids(parent=user.key, size=1)[0]
    token = AuthToken(key=key, type="p")
    token_key = token.put()
    return token_key


def send_password_reset_email(user, token_key):
    password_reset_url = url_for(
        ".reset_password",
        token_key=token_key.urlsafe().decode("utf-8"),
        _external=True,
    )
    logger.debug("Generated password reset url for %s", user.email)

    template_values = {
        "user": user,
        "password_reset_url": password_reset_url,
    }
    email_html = render_template("auth/forgot-email.html", **template_values)

    settings = Settings.get_config()
    email_provider = get_email_provider(settings)
    response = email_provider.send_email(
        from_email=Email(email="recognition@nydkc.org", name="NYDKC Awards Committee"),
        to_email=Email(email=user.email),
        subject=Subject(line="Resetting your DKC Application Password"),
        html_content=HtmlContent(content=email_html),
        custom_args=CustomArgs(
            metadata=(
                {
                    "dkc_purpose": "password_reset",
                }
            )
        ),
    )

    if not response.success:
        logger.error("Error sending email to %s: %s", user.email, response.errors)
        return abort(503)
