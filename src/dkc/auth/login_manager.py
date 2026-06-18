import functools

from flask import redirect, url_for
from flask_login import current_user, LoginManager, login_required
from google.cloud import ndb
from .models import User

g_login_manager = LoginManager()


@g_login_manager.user_loader
def load_user(user_id: str):
    return User.find_by_auth_credential_id(user_id)


@g_login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("auth.login"))


def anonymous_only(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for("application.overview"))
        else:
            return f(*args, **kwargs)

    return decorated_function
