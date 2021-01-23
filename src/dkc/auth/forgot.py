import json
import logging
from flask import abort, render_template, request, url_for
from flask_wtf import FlaskForm, Recaptcha, RecaptchaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email
from google.cloud import ndb
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    CustomArg,
    From,
    HtmlContent,
    Mail,
    Subject,
    To,
)
from common.models import Settings
from .login_manager import anonymous_only
from .models import User, AuthToken
from . import auth_bp


class ForgetForm(FlaskForm):
    email = EmailField("email", [Email("Please enter a valid email address.")])
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
            logging.warning("Could not find any user for email: %s", email)
            form.email.errors.append("No account found with email '%s'.".format(email))
        else:
            token_key = create_password_reset_auth_token(user)
            send_password_reset_email(user, token_key)
            template_values["forgot_email_sent_to"] = email

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
    logging.debug("Generated password reset url for %s", user.email)

    template_values = {
        "user": user,
        "password_reset_url": password_reset_url,
    }
    email_html = render_template("auth/forgot-email.html", **template_values)

    settings = ndb.Key(Settings, "config").get()
    sg = SendGridAPIClient(api_key=settings.sendgrid_api_key)
    message = Mail(
        from_email=From("recognition@nydkc.org", "NYDKC Awards Committee"),
        to_emails=To(user.email),
        subject=Subject("Resetting your DKC Application Password"),
        html_content=HtmlContent(email_html),
    )
    message.custom_arg = [
        CustomArg(key="dkc_purpose", value="password_reset"),
    ]

    response = sg.client.mail.send.post(request_body=message.get())
    if response.status_code != 202:
        json_response = json.loads(response.body)
        logging.error(
            "Error sending email to %s: %s", message.to, json_response["errors"]
        )
        return abort(503)
