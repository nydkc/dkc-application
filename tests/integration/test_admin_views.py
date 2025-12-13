import pytest
from datetime import datetime
import time
import uuid
from google.cloud import ndb
from unittest.mock import patch, MagicMock
from admin.auth.models import AdminUser, OAuth2Token
from dkc.application.models import Application
from dkc.auth.models import User
from common.models import Settings
from common.timezone import Eastern, UTC
from admin.auth.authlib_oauth import g_oauth
from admin.dashboard import query_helpers
from tests.helpers import wait_for_datastore_consistency


@pytest.fixture
def admin_user(ndb_context):
    email = f"admin_{uuid.uuid4().hex}@example.com"
    user = AdminUser(email=email)
    user.oauth2_token = OAuth2Token(expires_at=int(time.time()) + 3600)
    user.put()
    return user


@pytest.fixture
def admin_logged_in(client, admin_user):
    with client.session_transaction() as sess:
        sess["admin_user"] = admin_user.key.id()

    with patch("admin.auth.login_manager.is_project_admin", return_value=True):
        yield client


def test_admin_dashboard_requires_login(client):
    response = client.get("/admin/overview")
    assert response.status_code == 302


def test_admin_login_flow(client, ndb_context):
    with patch("admin.auth.login.g_oauth") as mock_oauth, patch(
        "admin.auth.login.is_project_admin", return_value=True
    ):

        mock_oauth.google.authorize_access_token.return_value = {
            "access_token": "fake",
            "expires_at": int(time.time()) + 3600,
            "token_type": "Bearer",
            "refresh_token": "fake_refresh",
        }
        mock_oauth.google.get.return_value.json.return_value = {
            "email": "admin@example.com",
            "picture": "pic.jpg",
        }
        mock_oauth.google.authorize_redirect.return_value = (
            "http://localhost/admin/login/google_oauth2callback"
        )

        response = client.get("/admin/login/google_oauth2callback")
        assert response.status_code == 302
        assert response.location.endswith("/admin/overview")

        with client.session_transaction() as sess:
            assert "admin_user" in sess


def test_admin_dashboard_overview(admin_logged_in):
    response = admin_logged_in.get("/admin/overview")
    assert response.status_code == 200
    assert b"DKC App Admin" in response.data


def test_admin_application_search(admin_logged_in, ndb_context):
    email = f"applicant_{uuid.uuid4().hex}@example.com"
    user = User(email=email, first_name="John", last_name="Doe")
    user_key = user.put()
    app = Application(parent=user_key)
    app.submit_time = datetime.now()
    app_key = app.put()

    user.application = app_key
    user.put()

    # Wait for datastore consistency
    def check_consistency():
        applicants, applications = query_helpers.get_all_search()
        for a, app_obj in zip(applicants, applications):
            if a.email == email and app_obj:
                return True
        return False

    wait_for_datastore_consistency(check_consistency)

    response = admin_logged_in.get("/admin/search?q=John")
    assert response.status_code == 200
    assert b"John Doe" in response.data


def test_admin_application_detail(admin_logged_in, ndb_context):
    email = f"applicant_{uuid.uuid4().hex}@example.com"
    user = User(email=email, first_name="John", last_name="Doe")
    user_key = user.put()
    app = Application(parent=user_key)
    app_key = app.put()

    user.application = app_key
    user.put()

    # Wait for datastore consistency
    def check_consistency():
        u, a = query_helpers.find_applicant_and_application_by_email(email)
        return u is not None and a is not None

    wait_for_datastore_consistency(check_consistency)

    url = f"/admin/show/{user.email}"
    response = admin_logged_in.get(url)
    assert response.status_code == 200
    assert b"John Doe" in response.data


def test_admin_application_detail_404(admin_logged_in):
    url = "/admin/show/nonexistent@example.com"
    response = admin_logged_in.get(url)
    assert response.status_code == 404
    assert b"Not Found" in response.data


def test_admin_settings_update(admin_logged_in, ndb_context):
    data = {
        "due_date": "1999-12-31T23:59:59",
        "awards_booklet_url": "http://example.com",
        "secret_key": "secret",
        "google_oauth_client_id": "id",
        "google_oauth_client_secret": "secret",
        "recaptcha_site_key": "key",
        "recaptcha_secret": "secret",
        "mailersend_api_key": "key",
        "maileroo_api_key": "key",
        "gcs_bucket": "bucket",
    }
    response = admin_logged_in.post("/admin/settings", data=data, follow_redirects=True)
    assert response.status_code == 200

    settings = Settings.get_config()
    # Ensure that datetime is stored in UTC
    assert settings.due_date.replace(tzinfo=UTC()).astimezone(tz=Eastern).year == 1999
    assert settings.due_date.replace(tzinfo=UTC()).astimezone(tz=Eastern).month == 12
    assert settings.due_date.replace(tzinfo=UTC()).astimezone(tz=Eastern).day == 31
    assert settings.due_date.replace(tzinfo=UTC()).astimezone(tz=Eastern).hour == 23
    assert settings.due_date.replace(tzinfo=UTC()).astimezone(tz=Eastern).minute == 59
    assert settings.due_date.replace(tzinfo=UTC()).astimezone(tz=Eastern).second == 59

def test_admin_application_delete(admin_logged_in, ndb_context):
    email = f"applicant_{uuid.uuid4().hex}@example.com"
    user = User(email=email)
    user_key = user.put()
    app = Application(parent=user_key)
    app_key = app.put()

    user.application = app_key
    user.put()

    # Wait for datastore consistency
    def check_consistency():
        u = query_helpers.find_applicant_by_email(email)
        return u is not None and u.application is not None

    wait_for_datastore_consistency(check_consistency)

    url = "/admin/danger_delete_applicants"
    data = {"email": [user.email]}
    response = admin_logged_in.post(url, data=data, follow_redirects=True)
    assert response.status_code == 200

    assert app_key.get() is None
