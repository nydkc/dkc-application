import pytest
from dkc.auth.models import User
from unittest.mock import MagicMock, patch
import uuid


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_application_page_requires_login(client):
    response = client.get("/application/profile")
    assert response.status_code == 302


def test_application_page_access(client):
    email = "test_app@example.com"

    # Mock finding user logic for login
    with patch("dkc.auth.models.User.find_by_email") as mock_find_email, \
         patch("dkc.auth.models.User.find_by_auth_credential_id") as mock_find_auth, \
         patch("admin.auth.login_manager.is_project_admin", return_value=False):

        mock_user = MagicMock(spec=User)
        mock_user.is_authenticated = True
        mock_user.is_active = True
        mock_user.is_anonymous = False
        mock_user.get_id.return_value = "test_auth_id"
        mock_user.verify_password.return_value = True
        mock_user.key.id.return_value = 123
        mock_user.auth_credential_id = "test_auth_id"

        # Mock application reference if accessed
        mock_user.application.get.return_value = MagicMock()

        mock_find_email.return_value = mock_user
        mock_find_auth.return_value = mock_user

        client.post(
            "/login",
            data={"email": email, "password": "password"},
            follow_redirects=True,
        )

        response = client.get("/application/profile")
        assert response.status_code == 200
