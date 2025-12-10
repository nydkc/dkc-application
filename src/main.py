import logging
import os
from flask import Flask
from common.models import Settings
from common.datastore import db, g_ndb_wsgi_middleware
from common.flask_error_handlers import register_error_handlers_to
from common.jinja_functions import (
    JINJA_OPTIONS,
    ADDITIONAL_JINJA_FILTERS,
    ADDITIONAL_JINJA_GLOBALS,
)
from common.logging import configure_logging
from common.talisman import g_flask_talisman_init_app
from dkc.auth.login_manager import g_login_manager
from dkc.views import register_blueprints_to as register_dkc_blueprints_to
from admin.auth.authlib_oauth import g_oauth
from admin.views import register_blueprints_to as register_admin_blueprints_to

configure_logging()

app = Flask(__name__, template_folder="templates", static_folder="static")

app.jinja_options = JINJA_OPTIONS
app.jinja_env.filters.update(ADDITIONAL_JINJA_FILTERS)
app.jinja_env.globals.update(ADDITIONAL_JINJA_GLOBALS)

# Match the 32MB request limit of AppEngine
# https://cloud.google.com/appengine/docs/standard/python3/how-requests-are-handled#quotas_and_limits
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024

if not os.getenv("GAE_ENV", "").startswith("standard"):
    # Local Execution.
    app.debug = True
    app.config["EXPLAIN_TEMPLATE_LOADING"] = False

app.wsgi_app = g_ndb_wsgi_middleware(app.wsgi_app)

g_flask_talisman_init_app(app)
g_login_manager.init_app(app)
g_oauth.init_app(app)

register_error_handlers_to(app)
register_dkc_blueprints_to(app)
register_admin_blueprints_to(app)

logging.info("Initialized Flask App: app.url_map=\n%s", app.url_map)

if __name__ == "__main__":
    with db.context():
        settings = Settings.get_config()
        app.secret_key = settings.secret_key
        app.config["RECAPTCHA_PUBLIC_KEY"] = settings.recaptcha_site_key
        app.config["RECAPTCHA_PRIVATE_KEY"] = settings.recaptcha_secret
        app.config["GOOGLE_CLIENT_ID"] = settings.google_oauth_client_id
        app.config["GOOGLE_CLIENT_SECRET"] = settings.google_oauth_client_secret

    app.run(host="localhost", port=8080, debug=True)
