from typing import Any, Dict, Optional
import abc
import dataclasses
import requests
from datetime import datetime, timedelta
from google.cloud import ndb
from mailersend import emails as _MSEmails
from maileroo import MailerooClient, EmailAddress
from common.models import Settings


@dataclasses.dataclass
class Email:
    email: str
    name: str = None


@dataclasses.dataclass
class Subject:
    line: str


@dataclasses.dataclass
class HtmlContent:
    content: str


@dataclasses.dataclass
class CustomArgs:
    # metadata with keys of {"dkc_application_key", "dkc_purpose"}
    metadata: Dict[str, str]


@dataclasses.dataclass
class Response:
    success: bool
    http_code: int
    errors: Optional[Any]


class EmailProvider(abc.ABC):
    provider_name: str

    @abc.abstractmethod
    def send_email(
        self,
        from_email: Email,
        to_email: Email,
        subject: Subject,
        html_content: HtmlContent,
        custom_args: CustomArgs,
    ) -> Response:
        pass

    def send_heartbeat_email(self) -> Response:
        """Sends a heartbeat email to keep the account active."""
        return self.send_email(
            from_email=Email(email="dkc-app@nydkc.org", name="NYDKC DKC Application"),
            to_email=Email(email="dkc-app@nydkc.org"),
            subject=Subject(line="DKC Application is still alive!"),
            html_content=HtmlContent(
                content=f"Hello! This email keeps the {self.provider_name} account active."
            ),
            custom_args=CustomArgs(
                metadata=(
                    {
                        "dkc_purpose": "heartbeat",
                    }
                )
            ),
        )


def get_email_provider(settings: Settings) -> EmailProvider:
    """Initializes the default email provider with API keys from settings."""
    return Maileroo(api_key=settings.maileroo_api_key)


class EmailProviderMessageMapping(ndb.Model):
    """Message IDs mapping back to the corresponding DKC application.

    This is used specifically for mapping bounced emails back to the
    application that requested for verification.
    """

    provider_name = ndb.StringProperty()
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    message_id = ndb.StringProperty()
    dkc_application_key = ndb.StringProperty()

    @classmethod
    def find_by_message_id(cls, provider_name: str, message_id: str):
        return (
            cls.query()
            .filter(cls.provider == provider_name and cls.message_id == message_id)
            .get()
        )

    @classmethod
    def delete_expired_mappings(cls, days_old: int) -> int:
        cutoff_time = datetime.now() - timedelta(days=days_old)
        expired_mappings_query = cls.query().filter(cls.timestamp < cutoff_time)
        message_id_keys = [key for key in expired_mappings_query.fetch(keys_only=True)]
        ndb.delete_multi(message_id_keys)
        return len(message_id_keys)


class MailerSend(EmailProvider):
    def __init__(self, api_key: str):
        self.provider_name = "MailerSend"
        self._api_key = api_key

    def send_email(
        self,
        from_email: Email,
        to_email: Email,
        subject: Subject,
        html_content: HtmlContent,
        custom_args: CustomArgs,
    ) -> Response:
        mailer = _MSEmails.NewEmail(self._api_key)
        mail_body = {}
        mailer.set_mail_from(
            {
                "name": from_email.name,
                "email": from_email.email,
            },
            mail_body,
        )
        mailer.set_mail_to(
            [
                {
                    "name": to_email.name if to_email.name else to_email.email,
                    "email": to_email.email,
                }
            ],
            mail_body,
        )
        mailer.set_subject(subject.line, mail_body)
        mailer.set_html_content(html_content.content, mail_body)
        # Request is manually sent since we need the X-Message-Id in the response header
        # response = mailer.send(mail_body)
        response = requests.post(
            f"{mailer.api_base}/email", headers=mailer.headers_default, json=mail_body
        )
        self._track_message_id(custom_args, response)
        return self._convert_response(response)

    def _track_message_id(
        self, custom_args: CustomArgs, response: requests.Response
    ) -> None:
        # Only track message id for verification emails
        if custom_args.metadata["dkc_purpose"] != "verification":
            return
        if response.status_code != 202:
            return
        EmailProviderMessageMapping(
            provider_name=self.provider_name,
            message_id=response.headers["X-Message-Id"],
            dkc_application_key=custom_args.metadata["dkc_application_key"],
        ).put()

    def _convert_response(self, response: requests.Response) -> Response:
        errors = None
        # Errors are only provided in non-202 response codes
        # https://developers.mailersend.com/api/v1/email.html#send-an-email
        if response.status_code != 202:
            body = response.json()
            errors = body.get("errors", body)
        return Response(
            success=response.status_code == 202,
            http_code=response.status_code,
            errors=errors,
        )


class Maileroo(EmailProvider):
    def __init__(self, api_key: str):
        self.provider_name = "Maileroo"
        self._api_key = api_key
        self.client = MailerooClient(api_key)

    def send_email(
        self,
        from_email: Email,
        to_email: Email,
        subject: Subject,
        html_content: HtmlContent,
        custom_args: CustomArgs,
    ) -> Response:
        try:
            reference_id = self.client.send_basic_email(
                {
                    "from": EmailAddress(from_email.email, from_email.name),
                    "to": [EmailAddress(to_email.email, to_email.name)],
                    "subject": subject.line,
                    "html": html_content.content,
                }
            )
            self._track_message_id(custom_args, reference_id)
            return Response(success=True, http_code=200, errors=None)
        except RuntimeError as e:
            # Error handling is done via exceptions in Maileroo client
            # https://pypi.org/project/maileroo/
            return Response(success=False, http_code=500, errors=str(e))

    def _track_message_id(self, custom_args: CustomArgs, reference_id: str) -> None:
        # Only track message id for verification emails
        if custom_args.metadata["dkc_purpose"] != "verification":
            return
        EmailProviderMessageMapping(
            provider_name=self.provider_name,
            message_id=reference_id,
            dkc_application_key=custom_args.metadata["dkc_application_key"],
        ).put()
