from flask_login import UserMixin
from google.cloud import ndb
from passlib.hash import bcrypt_sha256


class User(ndb.Model, UserMixin):
    creation_time = ndb.DateTimeProperty(auto_now_add=True)
    updated_time = ndb.DateTimeProperty(auto_now=True)
    email = ndb.StringProperty()
    password_hash = ndb.StringProperty()

    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    application = ndb.KeyProperty()

    # Alternative id for identifying this user with their given credentials.
    # Used by Flask-Login to invalidate sessions after resetting password.
    auth_credential_id = ndb.StringProperty()

    @classmethod
    def hash_password(cls, password: str) -> str:
        return bcrypt_sha256.hash(password)

    def verify_password(self, password: str) -> bool:
        return bcrypt_sha256.verify(password, self.password_hash)

    @classmethod
    def find_by_auth_credential_id(cls, user_id: str):
        return cls.query().filter(cls.auth_credential_id == user_id).get()

    @classmethod
    def find_by_email(cls, email: str):
        return cls.query().filter(cls.email == email).get()

    @classmethod
    def get_authenticated_user(cls, email: str, password: str):
        user = cls.find_by_email(email)
        if user is None:
            return None
        if user.verify_password(password):
            return user
        else:
            return None

    def get_id(self):
        """ID used by flask-login"""
        return self.auth_credential_id

    def _get_unique_attributes_id(self):
        return "User.email:{}".format(self.email)


class UniqueUserTracking(ndb.Model):
    """Model class to track unique attributes of users.

    The ID of each entity corresponds to value of User._get_unique_attributes_id.
    """

    pass


class AuthToken(ndb.Model):
    """AuthTokens that are associated with a user."""

    created = ndb.DateTimeProperty(auto_now_add=True)
    type = ndb.StringProperty()
