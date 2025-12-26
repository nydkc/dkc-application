import pytest
import json
from unittest.mock import patch, MagicMock
from dkc.auth.models import User
from dkc.application.models import Application
from common.email_provider import EmailProviderMessageMapping
from dkc.application_verification.bounce import on_verification_bounce_event

@pytest.fixture
def mock_ndb_context():
    """Mocks NDB context and models."""
    with patch("common.email_provider.EmailProviderMessageMapping.query") as mock_mapping_query, \
         patch("dkc.auth.models.User.put") as mock_user_put, \
         patch("dkc.application.models.Application.put") as mock_app_put, \
         patch("google.cloud.ndb.Key") as mock_key_cls, \
         patch("google.cloud.ndb.context.Context.transaction", side_effect=lambda callback, **kwargs: callback()):

        yield {
            "mapping_query": mock_mapping_query,
            "user_put": mock_user_put,
            "app_put": mock_app_put,
            "key_cls": mock_key_cls,
        }

def test_mailersend_webhook_bounce(client, mock_ndb_context):
    mapping_key = MagicMock()
    app_key = MagicMock()
    app_key.urlsafe.return_value.decode.return_value = "app_key_urlsafe"

    # Use generic MagicMock to avoid property descriptor issues
    mock_app = MagicMock()
    mock_app.verification_ltg_sent = True
    mock_app.verification_ltg_email = "ltg@example.com"
    app_key.get.return_value = mock_app

    # Mock Key() constructor used in bounce.py to reconstruct keys
    mock_ndb_context["key_cls"].return_value = app_key

    # Mock finding the mapping: EmailProviderMessageMapping.query(...).get()
    mock_mapping = MagicMock()
    mock_mapping.dkc_application_key = "app_key_urlsafe"
    mock_ndb_context["mapping_query"].return_value.filter.return_value.get.return_value = mock_mapping

    on_verification_bounce_event("ltg@example.com", "app_key_urlsafe")

    assert mock_app.verification_ltg_sent is False
    assert "FAILED TO SEND EMAIL TO: ltg@example.com" == mock_app.verification_ltg_email
    assert mock_app.put.called


def test_maileroo_webhook_bounce(client, mock_ndb_context):
    app_key = MagicMock()
    app_key.urlsafe.return_value.decode.return_value = "app_key_urlsafe"

    mock_app = MagicMock()
    mock_app.verification_club_president_sent = True
    mock_app.verification_club_president_email = "pres@example.com"
    app_key.get.return_value = mock_app

    mock_ndb_context["key_cls"].return_value = app_key

    on_verification_bounce_event("pres@example.com", "app_key_urlsafe")

    assert mock_app.verification_club_president_sent is False
    assert "FAILED TO SEND EMAIL TO: pres@example.com" == mock_app.verification_club_president_email
    assert mock_app.put.called


def test_mailersend_webhook_unknown_message(client, caplog, mock_ndb_context):
    mock_ndb_context["mapping_query"].return_value.filter.return_value.get.return_value = None

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
        assert "Did not find mapping for MailerSend message ID: unknown_id" in caplog.text


def test_maileroo_webhook_unknown_message(client, caplog, mock_ndb_context):
    mock_ndb_context["mapping_query"].return_value.filter.return_value.get.return_value = None

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
