import pytest
from dkc.auth.models import User
import uuid
import time


def test_user_creation(ndb_context):
    user = User(email="test@example.com", first_name="Test", last_name="User")
    assert user.email == "test@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"


def test_password_hashing():
    password = "secret_password"
    hashed = User.hash_password(password)
    assert hashed != password
    assert User(password_hash=hashed).verify_password(password) is True
    assert User(password_hash=hashed).verify_password("wrong_password") is False


def test_get_authenticated_user(ndb_context):
    email = "auth_test@example.com"
    password = "password123"
    user = User(email=email, password_hash=User.hash_password(password))
    user.put()

    authenticated_user = User.get_authenticated_user(email, password)
    assert authenticated_user is not None
    assert authenticated_user.email == email

    assert User.get_authenticated_user(email, "wrong") is None
    assert User.get_authenticated_user("nonexistent@example.com", password) is None


def test_find_by_methods(ndb_context):
    unique_id = uuid.uuid4().hex
    email = f"find_me_{unique_id}@example.com"
    auth_id = f"unique_auth_id_{unique_id}"
    user = User(email=email, auth_credential_id=auth_id)
    user.put()

    found_by_email = None
    for _ in range(5):
        found_by_email = User.find_by_email(email)
        if found_by_email:
            break
        time.sleep(0.5)

    assert found_by_email is not None
    assert found_by_email.key.urlsafe() == user.key.urlsafe()

    found_by_id = User.find_by_auth_credential_id(auth_id)
    assert found_by_id is not None
    assert found_by_id.key.urlsafe() == user.key.urlsafe()


def test_get_id(ndb_context):
    auth_id = "my_flask_login_id"
    user = User(auth_credential_id=auth_id)
    assert user.get_id() == auth_id
