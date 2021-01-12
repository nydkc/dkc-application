from flask_login import UserMixin
from google.cloud import ndb


class User(ndb.Model, UserMixin):
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    email = ndb.StringProperty()
    password_hash = ndb.StringProperty()

    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    application = ndb.KeyProperty()

    # Alternative id for identifying this user with their given credentials.
    # Used by Flask-Login to invalidate sessions after resetting password.
    auth_credential_id = ndb.StringProperty()

    @classmethod
    def find_by_auth_credential_id(cls, user_id: str):
        return cls.query().filter(cls.auth_credential_id == user_id).get()

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
