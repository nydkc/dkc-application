import pytest
from unittest.mock import patch, MagicMock
from dkc.auth.models import User
from dkc.application.models import Application
from common.datastore import db


def test_verification_page_access(client, login, mock_user):
    response = client.get("/application/verification")
    assert response.status_code == 200
    assert b"Verification" in response.data


def test_send_verification_email(client, login, mock_user, mock_email_provider):
    with patch(
        "dkc.application.verification.get_email_provider",
        return_value=mock_email_provider,
    ) as mock_get_provider, patch(
        "dkc.application.verification.create_verification_auth_token"
    ) as mock_create_token:

        mock_token_key = MagicMock()
        mock_token_key.urlsafe.return_value = b"safe_token_key"
        mock_create_token.return_value = mock_token_key

        response = client.post(
            "/application/verification",
            data={"task": "ltg", "ltg-email": "ltg@example.com"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert mock_email_provider.send_email.called

        call_args = mock_email_provider.send_email.call_args
        assert call_args is not None
        kwargs = call_args[1]
        assert kwargs["to_email"].email == "ltg@example.com"
        assert "Distinguished Key Clubber Application" in kwargs["subject"].line


def test_verification_incomplete_profile(client, login, mock_user):
    mock_user.application.get.return_value.school = None

    response = client.post(
        "/application/verification",
        data={"task": "ltg", "ltg-email": "ltg@example.com"},
        follow_redirects=True,
    )

    assert response.status_code == 400


def test_verification_after_submission(client, login, mock_user):
    mock_user.application.get.return_value.submit_time = MagicMock()

    response = client.post(
        "/application/verification",
        data={"task": "ltg", "ltg-email": "ltg@example.com"},
        follow_redirects=True,
    )

    assert response.status_code == 409


def test_verification_invalid_task(client, login, mock_user):
    with patch(
        "dkc.application.verification.create_verification_auth_token"
    ) as mock_create_token:

        mock_token_key = MagicMock()
        mock_token_key.urlsafe.return_value = b"safe_token_key"
        mock_create_token.return_value = mock_token_key

        response = client.post(
            "/application/verification",
            data={"task": "invalid-task", "email": "test@example.com"},
            follow_redirects=True,
        )

        assert response.status_code == 400
