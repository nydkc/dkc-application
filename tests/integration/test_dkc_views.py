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


def test_application_page_access(client, app):
    unique_id = uuid.uuid4().hex
    email = f"test_app_{unique_id}@example.com"

    user = User(email=email, password_hash=User.hash_password("password"))
    user.auth_credential_id = "test_auth_id"
    user.put()

    with patch("dkc.auth.models.User.get_authenticated_user") as mock_auth, patch(
        "dkc.auth.models.User.find_by_auth_credential_id"
    ) as mock_find:

        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.is_active = True
        mock_user.is_anonymous = False
        mock_user.get_id.return_value = "test_auth_id"

        mock_auth.return_value = mock_user
        mock_find.return_value = mock_user

        client.post(
            "/login",
            data={"email": email, "password": "password"},
            follow_redirects=True,
        )

        response = client.get("/application/profile")
        assert response.status_code == 200
