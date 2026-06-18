from dkc.auth.models import User
from common.datastore import db
from unittest.mock import patch, MagicMock
import uuid


def test_login_page_loads(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data


def test_login_submission(client):
    email = "test@example.com"
    password = "password"

    with patch("dkc.auth.models.User.get_authenticated_user") as mock_auth:
        unique_id = uuid.uuid4().hex
        email = f"test_{unique_id}@example.com"

        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.is_active = True
        mock_user.is_anonymous = False
        mock_user.get_id.return_value = "test_id"
        mock_user.application = MagicMock()
        mock_user.application.get.return_value = MagicMock()

        mock_auth.return_value = mock_user

        response = client.post(
            "/login", data={"email": email, "password": password}, follow_redirects=True
        )

    assert response.status_code == 200


def test_logout(client):
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
