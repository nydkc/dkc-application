from flask_login import UserMixin
from google.cloud import ndb

class User(ndb.Model, UserMixin):
    email = ndb.StringProperty()
    # TODO(dannyqiu): remove this field
    password = ndb.StringProperty()
    password_hash = ndb.StringProperty()
    date_created = ndb.DateTimeProperty()
