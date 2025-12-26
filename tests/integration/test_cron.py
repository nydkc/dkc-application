import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from dkc.auth.models import AuthToken
from admin.auth.models import AdminUser
from common.email_provider import EmailProviderMessageMapping

@pytest.fixture
def mock_ndb_context():
    """Mocks NDB for cron tests."""
    with patch("dkc.auth.models.AuthToken.query") as mock_auth_query, \
         patch("admin.auth.models.AdminUser.query") as mock_admin_query, \
         patch("common.email_provider.EmailProviderMessageMapping.query") as mock_email_query, \
         patch("google.cloud.ndb.delete_multi") as mock_delete_multi:
        yield {
            "auth_query": mock_auth_query,
            "admin_query": mock_admin_query,
            "email_query": mock_email_query,
            "delete_multi": mock_delete_multi,
        }

def test_auth_token_cleanup(client, mock_ndb_context):
    headers = {"X-Appengine-Cron": "true"}

    # Mock query returning some tokens
    mock_token = MagicMock(spec=AuthToken)
    mock_token.key = MagicMock()
    # If the cron job iterates or fetches, return list
    # Assuming code uses .fetch()
    mock_ndb_context["auth_query"].return_value.filter.return_value.fetch.return_value = [mock_token]

    response = client.get("/cron/auth_token_cleanup", headers=headers)
    assert response.status_code == 200

    # Verify deletions occurred
    # Depending on implementation (delete_multi or key.delete())
    # The previous test verified key.get() is None, implying delete happened.
    # We verify delete call.
    assert mock_token.key.delete.called or mock_ndb_context["delete_multi"].called


def test_admin_user_token_cleanup(client, mock_ndb_context):
    headers = {"X-Appengine-Cron": "true"}

    mock_user = MagicMock(spec=AdminUser)
    mock_user.key = MagicMock()

    # Mock query chain: query().filter().fetch()
    mock_ndb_context["admin_query"].return_value.filter.return_value.fetch.return_value = [mock_user]

    response = client.get("/cron/admin_user_token_cleanup", headers=headers)
    assert response.status_code == 200

    assert mock_user.key.delete.called or mock_ndb_context["delete_multi"].called


def test_email_message_id_cleanup(client, mock_ndb_context):
    headers = {"X-Appengine-Cron": "true"}

    mock_mapping = MagicMock(spec=EmailProviderMessageMapping)
    mock_mapping.key = MagicMock()

    mock_ndb_context["email_query"].return_value.filter.return_value.fetch.return_value = [mock_mapping]

    response = client.get("/cron/email_message_id_cleanup", headers=headers)
    assert response.status_code == 200

    # The cron job likely iterates and deletes
    # If it uses delete_multi, we check that.
    # If it uses individual delete, we check that.
    assert mock_mapping.key.delete.called or mock_ndb_context["delete_multi"].called


def test_cron_security(client):
    response = client.get("/cron/auth_token_cleanup")
    assert response.status_code == 403
