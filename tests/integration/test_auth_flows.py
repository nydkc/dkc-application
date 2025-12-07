import pytest
from unittest.mock import patch, MagicMock
from dkc.auth.models import User, AuthToken
from dkc.application.models import Application
from common.datastore import db
import uuid
import time


def test_registration_page_access(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Register" in response.data


def test_registration_submission(client, ndb_context):
    unique_id = uuid.uuid4().hex
    email = f"newuser_{unique_id}@example.com"
    password = "newpassword"
    first_name = "New"
    last_name = "User"

    response = client.post(
        "/register",
        data={
            "email": email,
            "password": password,
            "confirm_password": password,
            "first_name": first_name,
            "last_name": last_name,
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    user = None
    for _ in range(5):
        user = User.find_by_email(email)
        if user:
            break
        time.sleep(0.5)

    assert user is not None
    assert user.first_name == first_name
    assert user.last_name == last_name
    assert user.verify_password(password)

    assert user.application is not None
    app = user.application.get()
    assert app is not None
    assert isinstance(app, Application)


def test_forgot_password_page_access(client):
    response = client.get("/forgot")
    assert response.status_code == 200
    assert b"Forgot Password" in response.data


def test_forgot_password_submission(client, ndb_context, mock_email_provider):
    unique_id = uuid.uuid4().hex
    email = f"forgot_{unique_id}@example.com"
    user = User(email=email, password_hash=User.hash_password("oldpass"))
    user.put()

    for _ in range(5):
        if User.find_by_email(email):
            break
        time.sleep(0.5)

    with patch(
        "dkc.auth.forgot.get_email_provider", return_value=mock_email_provider
    ) as mock_get_provider:

        response = client.post("/forgot", data={"email": email}, follow_redirects=True)

        assert response.status_code == 200
        assert mock_email_provider.send_email.called

        token = AuthToken.query(AuthToken.type == "p").get()
        assert token is not None


def test_reset_password_flow(client, ndb_context):
    unique_id = uuid.uuid4().hex
    email = f"reset_{unique_id}@example.com"
    old_password = "oldpass"
    user = User(email=email, password_hash=User.hash_password(old_password))
    user.put()

    for _ in range(5):
        if User.find_by_email(email):
            break
        time.sleep(0.5)

    token = AuthToken(parent=user.key, type="p")
    token.put()
    token_key = token.key.urlsafe().decode("utf-8")

    response = client.get(f"/reset-password/p/{token_key}")
    assert response.status_code == 200
    assert b"Reset Password" in response.data

    new_password = "newpassword123"
    response = client.post(
        f"/reset-password/p/{token_key}",
        data={"password": new_password, "confirm_password": new_password},
        follow_redirects=True,
    )

    assert response.status_code == 200

    updated_user = user.key.get()
    assert updated_user.verify_password(new_password)
    assert not updated_user.verify_password(old_password)

    assert token.key.get() is None
