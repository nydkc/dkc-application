import pytest
import json
import uuid
from unittest.mock import patch, MagicMock
from dkc.auth.models import User
from dkc.application.models import Application
from dkc.application_verification.bounce import on_verification_bounce_event
from common.email_provider import EmailProviderMessageMapping


def test_mailersend_webhook_bounce(client, ndb_context):
    email = f"applicant_{uuid.uuid4().hex}@example.com"
    user = User(email=email)
    user_key = user.put()

    app = Application(parent=user_key)
    app.verification_ltg_email = "ltg@example.com"
    app.verification_ltg_sent = True
    app_key = app.put()

    mapping = EmailProviderMessageMapping(
        provider_name="MailerSend",
        message_id="ms_msg_id",
        dkc_application_key=app_key.urlsafe().decode("utf-8"),
    )
    mapping.put()

    payload = {
        "type": "activity.soft_bounced",
        "data": {
            "email": {
                "message": {"id": "ms_msg_id"},
                "recipient": {"email": "ltg@example.com"},
            }
        },
    }

    on_verification_bounce_event("ltg@example.com", app_key.urlsafe().decode("utf-8"))

    updated_app = app_key.get()
    assert updated_app.verification_ltg_sent is False
    assert (
        "FAILED TO SEND EMAIL TO: ltg@example.com" == updated_app.verification_ltg_email
    )


def test_maileroo_webhook_bounce(client, ndb_context):
    email = f"applicant_{uuid.uuid4().hex}@example.com"
    user = User(email=email)
    user_key = user.put()

    app = Application(parent=user_key)
    app.verification_club_president_email = "pres@example.com"
    app.verification_club_president_sent = True
    app_key = app.put()

    mapping = EmailProviderMessageMapping(
        provider_name="Maileroo",
        message_id="mr_msg_id",
        dkc_application_key=app_key.urlsafe().decode("utf-8"),
    )
    mapping.put()

    payload = {
        "event_type": "failed",
        "message_reference_id": "mr_msg_id",
        "event_data": {"to": "pres@example.com"},
    }

    on_verification_bounce_event("pres@example.com", app_key.urlsafe().decode("utf-8"))

    updated_app = app_key.get()
    assert updated_app.verification_club_president_sent is False
    assert (
        "FAILED TO SEND EMAIL TO: pres@example.com"
        == updated_app.verification_club_president_email
    )


def test_mailersend_webhook_unknown_message(client, caplog):
    payload = {
        "type": "activity.soft_bounced",
        "data": {
            "email": {
                "message": {"id": "unknown_id"},
                "recipient": {"email": "test@example.com"},
            }
        },
    }

    with caplog.at_level("ERROR"):
        response = client.post(
            "/mailersend/event",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 200
        assert (
            "Did not find mapping for MailerSend message ID: unknown_id" in caplog.text
        )


def test_maileroo_webhook_unknown_message(client, caplog):
    payload = {
        "event_type": "failed",
        "message_reference_id": "unknown_id",
        "event_data": {"to": "test@example.com"},
    }

    with caplog.at_level("ERROR"):
        response = client.post(
            "/maileroo/event", data=json.dumps(payload), content_type="application/json"
        )
        assert response.status_code == 200
        assert "Did not find mapping for Maileroo message ID: unknown_id" in caplog.text
