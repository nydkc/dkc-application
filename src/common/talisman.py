import os
from flask_talisman import Talisman


def g_flask_talisman_init_app(app):
    Talisman(app, content_security_policy=None)
