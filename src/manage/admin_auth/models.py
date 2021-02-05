import time
from google.cloud import ndb


class OAuth2Token(ndb.Model):
    provider = ndb.StringProperty(default="google")
    token_type = ndb.StringProperty()
    access_token = ndb.StringProperty()
    refresh_token = ndb.StringProperty()
    expires_at = ndb.IntegerProperty()

    def requires_refresh(self) -> bool:
        return self.expires_at < time.time()


class AdminUser(ndb.Model):
    email = ndb.StringProperty()
    picture_url = ndb.StringProperty()
    oauth2_token = ndb.StructuredProperty(OAuth2Token)

    @classmethod
    def find_by_email(cls, email: str):
        return cls.query().filter(cls.email == email).get()

    def get_auth_id(self):
        return self.key.id()

    @staticmethod
    def get_by_auth_id(id):
        return AdminUser.get_by_id(id)
