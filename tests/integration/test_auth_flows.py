import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from dkc.auth.models import User, AuthToken, UniqueUserTracking
from dkc.application.models import Application
import uuid
import time

@pytest.fixture
def mock_ndb_context():
    """Mocks NDB context and models commonly used in auth flows."""
    with patch("dkc.auth.models.User.query") as mock_user_query, \
         patch("dkc.auth.models.User.find_by_email") as mock_find_by_email, \
         patch("dkc.auth.models.User.put") as mock_user_put, \
         patch("dkc.auth.models.AuthToken.query") as mock_token_query, \
         patch("dkc.auth.models.AuthToken.put") as mock_token_put, \
         patch("dkc.application.models.Application.put") as mock_app_put, \
         patch("google.cloud.ndb.Key") as mock_key_cls, \
         patch("google.cloud.ndb.context.Context.transaction", side_effect=lambda callback, **kwargs: callback()):

        yield {
            "user_query": mock_user_query,
            "find_by_email": mock_find_by_email,
            "user_put": mock_user_put,
            "token_query": mock_token_query,
            "token_put": mock_token_put,
            "app_put": mock_app_put,
            "key_cls": mock_key_cls,
        }

def test_registration_page_access(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Register" in response.data


def test_registration_submission(client, mock_ndb_context):
    email = "newuser@example.com"
    password = "newpassword"
    first_name = "New"
    last_name = "User"

    # Patch the service function to avoid NDB transaction issues
    with patch("dkc.auth.register.create_user_application") as mock_create:
        mock_user = MagicMock(spec=User)
        mock_user.first_name = first_name
        mock_user.last_name = last_name
        mock_user.email = email
        mock_create.return_value = mock_user

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
    assert mock_create.called
    args, _ = mock_create.call_args
    assert args == (email, password, first_name, last_name)


def test_registration_duplicate_email(client, mock_ndb_context):
    """Test that registering with an existing email fails."""
    email = "duplicate@example.com"

    # Patch service function to raise error
    with patch("dkc.auth.register.create_user_application") as mock_create:
        from dkc.auth.register import EmailAlreadyExistsError
        mock_create.side_effect = EmailAlreadyExistsError()

        response = client.post(
            "/register",
            data={
                "email": email,
                "password": "password123",
                "confirm_password": "password123",
                "first_name": "First",
                "last_name": "User",
            },
            follow_redirects=True,
        )
    assert response.status_code == 200
    assert b"is already taken" in response.data


def test_registration_password_length(client):
    """Test that password meets length requirements."""
    response = client.post(
        "/register",
        data={
            "email": "shortpass@example.com",
            "password": "short",
            "confirm_password": "short",
            "first_name": "Short",
            "last_name": "Pass",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Your password must be at least 8 characters" in response.data


def test_forgot_password_page_access(client):
    response = client.get("/forgot")
    assert response.status_code == 200
    assert b"Forgot Password" in response.data


def test_forgot_password_submission(client, mock_ndb_context, mock_email_provider):
    email = "forgot@example.com"

    mock_user = MagicMock(spec=User)
    mock_user.key = MagicMock()
    mock_ndb_context["find_by_email"].return_value = mock_user

    with patch(
        "dkc.auth.forgot.get_email_provider", return_value=mock_email_provider
    ) as mock_get_provider, \
    patch("dkc.auth.forgot.create_password_reset_auth_token") as mock_create_token:

        # mock_create_token must return a token_key that has urlsafe().decode()
        mock_key = MagicMock()
        mock_key.urlsafe.return_value.decode.return_value = "safe_token"
        mock_create_token.return_value = mock_key

        response = client.post("/forgot", data={"email": email}, follow_redirects=True)

        assert response.status_code == 200
        assert mock_email_provider.send_email.called
        assert mock_create_token.called



def test_reset_password_flow(client, mock_ndb_context):
    token_urlsafe = "fake_token_urlsafe"

    # Mock ndb.Key(urlsafe=...) to return a key
    mock_key = MagicMock()
    mock_ndb_context["key_cls"].return_value = mock_key

    # Mock token retrieval
    mock_token = MagicMock(spec=AuthToken)
    mock_token.type = "p"
    # Mock token.key.parent().get() -> user
    mock_user = MagicMock(spec=User)
    mock_token.key.parent.return_value.get.return_value = mock_user

    mock_key.get.return_value = mock_token

    # Patch helper functions to avoid NDB and isinstance checks
    with patch("dkc.auth.reset_password.decode_auth_token_with_type") as mock_decode, \
         patch("dkc.auth.reset_password.update_password") as mock_update:

        mock_decode.return_value = mock_token

        response = client.get(f"/reset-password/p/{token_urlsafe}")
        assert response.status_code == 200
        assert b"Reset Password" in response.data

        new_password = "newpassword123"
        response = client.post(
            f"/reset-password/p/{token_urlsafe}",
            data={"password": new_password, "confirm_password": new_password},
            follow_redirects=True,
        )

        assert response.status_code == 200

        # Verify update_password called
        assert mock_update.called


def test_login_failure(client, mock_ndb_context):
    """Test login with incorrect credentials."""
    email = "login_fail@example.com"

    # Mock find_by_email to return user
    mock_user = MagicMock(spec=User)
    mock_user.password_hash = "hashed_pw"
    # Mock verify_password to return False
    mock_user.verify_password.return_value = False

    mock_ndb_context["find_by_email"].return_value = mock_user

    # Test incorrect password
    response = client.post(
        "/login",
        data={"email": email, "password": "wrong_password"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Login failed!" in response.data

    # Test non-existent user
    mock_ndb_context["find_by_email"].return_value = None
    response = client.post(
        "/login",
        data={"email": "nonexistent@example.com", "password": "any_password"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Login failed!" in response.data


def test_logout(client, mock_ndb_context):
    """Test logout functionality."""
    email = "logout@example.com"
    password = "password123"

    # Mock successful login
    mock_user = MagicMock(spec=User)
    mock_user.verify_password.return_value = True
    mock_user.key.id.return_value = 123
    mock_user.auth_credential_id = "test_cred_id"
    mock_user.get_id.return_value = "test_cred_id" # Fix for TypeError
    mock_user.application.get.return_value = MagicMock() # For overview redirect check

    mock_ndb_context["find_by_email"].return_value = mock_user

    # Login
    response = client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )

    # Verify session set
    with client.session_transaction() as sess:
        assert "_user_id" in sess

    # Logout
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200

    # Verify logged out
    with client.session_transaction() as sess:
        assert "_user_id" not in sess
