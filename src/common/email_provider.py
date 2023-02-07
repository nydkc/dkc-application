from typing import Any, Dict, List
import abc
import dataclasses
from sendgrid import SendGridAPIClient as _SendGridAPIClient
from sendgrid.helpers import mail as _SGMail
from python_http_client.client import Response as _SGResponse


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
    errors: List[Any]


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


class SendGrid(EmailProvider):
    def __init__(self, api_key: str):
        self.provider = "SendGrid"
        self._client = _SendGridAPIClient(api_key=api_key)

    def send_email(
        self,
        from_email: Email,
        to_email: Email,
        subject: Subject,
        html_content: HtmlContent,
        custom_args: CustomArgs,
    ) -> Response:
        message = _SGMail.Mail(
            from_email=_SGMail.From(email=from_email.email, name=from_email.name),
            to_emails=_SGMail.To(email=to_email.email, name=to_email.name),
            subject=_SGMail.Subject(subject.line),
            html_content=html_content.content,
        )
        message.custom_arg = [
            _SGMail.CustomArg(key=k, value=v) for k, v in custom_args.metadata.items()
        ]
        resp = self._client.send(message)
        return self._convert_response(resp)

    def _convert_response(self, response: _SGResponse) -> Response:
        errors = []
        # Errors are only provided in non-202 response codes
        # https://docs.sendgrid.com/api-reference/mail-send/mail-send#responses
        if response.status_code != 202:
            body = response.to_dict()
            if "errors" in body:
                errors = body["errors"]
        return Response(http_code=response.status_code, errors=errors)
