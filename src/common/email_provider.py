from typing import Any, Dict, Optional
import abc
import dataclasses
import requests
from google.cloud import ndb
from mailersend import emails as _MSEmails


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
    metadata: Dict[str, str]


@dataclasses.dataclass
class Response:
    http_code: int
    errors: Optional[Any]


class EmailProvider(abc.ABC):
    provider: str

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


class MailerSendMessageId(ndb.Model):
    """Message IDs mapping back to the corresponding DKC application.

    This is used specifically for mapping bounced emails back to the
    application that requested for verification.
    """

    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    message_id = ndb.StringProperty()
    dkc_application_key = ndb.StringProperty()

    @classmethod
    def find_by_message_id(cls, message_id: str):
        return cls.query().filter(cls.message_id == message_id).get()


class MailerSend(EmailProvider):
    def __init__(self, api_key: str):
        self.provider = "MailerSend"
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
        MailerSendMessageId(
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
        return Response(http_code=response.status_code, errors=errors)
