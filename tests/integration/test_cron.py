import pytest
from datetime import datetime, timedelta
import time
from dkc.auth.models import AuthToken
from admin.auth.models import AdminUser, OAuth2Token
from common.email_provider import EmailProviderMessageMapping
from common.constants import AUTH_TOKEN_VALIDITY_DAYS


def test_auth_token_cleanup(client, ndb_context):
    valid_token = AuthToken(type="p")
    valid_token.put()

    expired_token = AuthToken(type="p")
    expired_token.put()
    expired_token.created = datetime.now() - timedelta(
        days=AUTH_TOKEN_VALIDITY_DAYS + 1
    )
    expired_token.put()

    headers = {"X-Appengine-Cron": "true"}
    response = client.get("/cron/auth_token_cleanup", headers=headers)
    assert response.status_code == 200

    assert valid_token.key.get() is not None
    assert expired_token.key.get() is None


def test_admin_user_token_cleanup(client, ndb_context):
    valid_user = AdminUser(email="valid@example.com")
    valid_user.oauth2_token = OAuth2Token(expires_at=int(time.time()) + 3600)
    valid_user.put()

    expired_user = AdminUser(email="expired@example.com")
    expired_user.oauth2_token = OAuth2Token(expires_at=int(time.time()) - 3600)
    expired_user.put()

    # Wait for consistency
    for _ in range(10):
        results = (
            AdminUser.query()
            .filter(AdminUser.oauth2_token.expires_at < int(time.time()))
            .fetch()
        )
        if any(r.key == expired_user.key for r in results):
            break
        time.sleep(0.5)

    headers = {"X-Appengine-Cron": "true"}
    response = client.get("/cron/admin_user_token_cleanup", headers=headers)
    assert response.status_code == 200

    assert valid_user.key.get() is not None
    assert expired_user.key.get() is None


def test_email_message_id_cleanup(client, ndb_context):
    valid_mapping = EmailProviderMessageMapping(
        provider_name="Test", message_id="valid_id", dkc_application_key="key"
    )
    valid_mapping.put()

    expired_mapping = EmailProviderMessageMapping(
        provider_name="Test", message_id="expired_id", dkc_application_key="key"
    )
    expired_mapping.put()
    expired_mapping.timestamp = datetime.now() - timedelta(days=2)
    expired_mapping.put()

    # Wait for consistency
    for _ in range(10):
        results = (
            EmailProviderMessageMapping.query()
            .filter(
                EmailProviderMessageMapping.timestamp
                < datetime.now() - timedelta(days=1)
            )
            .fetch()
        )
        if any(r.key == expired_mapping.key for r in results):
            break
        time.sleep(0.5)

    headers = {"X-Appengine-Cron": "true"}
    response = client.get("/cron/email_message_id_cleanup", headers=headers)
    assert response.status_code == 200

    assert valid_mapping.key.get() is not None
    assert expired_mapping.key.get() is None


def test_cron_security(client):
    response = client.get("/cron/auth_token_cleanup")
    assert response.status_code == 403
