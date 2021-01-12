from flask_login import LoginManager
from google.cloud import ndb
from . import models

g_login_manager = LoginManager()

@g_login_manager.user_loader
def load_user(user_id: str):
    return models.User.find_by_auth_credential_id(user_id)
