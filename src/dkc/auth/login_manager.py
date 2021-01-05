from flask_login import LoginManager
from google.cloud import ndb
from . import models

g_login_manager = LoginManager()

@g_login_manager.user_loader
def load_user(user_id: str):
    return ndb.Key(models.User.__name__, user_id).get()
