import logging
from flask import Flask, render_template
from google.cloud import ndb

from common.constants import GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET, RECAPTCHA_SECRET, RECAPTCHA_SITE_KEY, SECRET_KEY
from common.datastore import g_ndb_wsgi_middleware
from common.flask_error_handlers import register_error_handlers_to
from common.jinja_functions import JINJA_OPTIONS, ADDITIONAL_JINJA_FILTERS, ADDITIONAL_JINJA_GLOBALS
from dkc.auth.login_manager import g_login_manager
from dkc.views import register_blueprints_to as register_dkc_blueprints_to
from manage.auth.authlib_oauth import g_oauth
from manage.views import register_blueprints_to as register_admin_blueprints_to

app = Flask(__name__, template_folder='templates', static_folder='static')

app.secret_key = SECRET_KEY
app.config['RECAPTCHA_PUBLIC_KEY'] = RECAPTCHA_SITE_KEY
app.config['RECAPTCHA_PRIVATE_KEY'] = RECAPTCHA_SECRET
app.config['GOOGLE_CLIENT_ID'] = GOOGLE_OAUTH_CLIENT_ID
app.config['GOOGLE_CLIENT_SECRET'] = GOOGLE_OAUTH_CLIENT_SECRET

app.jinja_options = JINJA_OPTIONS
app.jinja_env.filters.update(ADDITIONAL_JINJA_FILTERS)
app.jinja_env.globals.update(ADDITIONAL_JINJA_GLOBALS)
app.config['EXPLAIN_TEMPLATE_LOADING'] = True

# Match the 32MB request limit of AppEngine
# https://cloud.google.com/appengine/docs/standard/python3/how-requests-are-handled#quotas_and_limits
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

app.wsgi_app = g_ndb_wsgi_middleware(app.wsgi_app)
g_login_manager.init_app(app)
g_oauth.init_app(app)

register_error_handlers_to(app)
register_dkc_blueprints_to(app)
register_admin_blueprints_to(app)

print(app.url_map)

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
