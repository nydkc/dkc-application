from flask import Flask, render_template
from google.cloud import ndb

from common.constants import RECAPTCHA_SECRET, RECAPTCHA_SITE_KEY, SECRET_KEY
from common.datastore import g_ndb_wsgi_middleware
from dkc.auth.login_manager import g_login_manager
from dkc.views import register_blueprints_to as register_dkc_blueprints_to
from dkc import JINJA_OPTIONS, ADDITIONAL_JINJA_FILTERS
# from manage.views import admin_blueprint

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = SECRET_KEY
app.config['RECAPTCHA_PUBLIC_KEY'] = RECAPTCHA_SITE_KEY
app.config['RECAPTCHA_PRIVATE_KEY'] = RECAPTCHA_SECRET
# app.testing = True
app.jinja_options = JINJA_OPTIONS
app.jinja_env.filters.update(ADDITIONAL_JINJA_FILTERS)
app.config['EXPLAIN_TEMPLATE_LOADING'] = True

app.wsgi_app = g_ndb_wsgi_middleware(app.wsgi_app)
g_login_manager.init_app(app)

register_dkc_blueprints_to(app)
# app.register_blueprint(admin_blueprint)

print(app.url_map)

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
