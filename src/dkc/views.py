from dkc.index import index_bp
from dkc.webhooks import webhooks_bp
from dkc.auth.views import auth_bp
from dkc.application.views import application_bp
from dkc.dummy.views import dummy_bp
from dkc.verify.views import verify_bp


def register_blueprints_to(app):
    app.register_blueprint(index_bp)
    app.register_blueprint(webhooks_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(application_bp, url_prefix="/application")
    app.register_blueprint(dummy_bp, url_prefix="/dummy")
    app.register_blueprint(verify_bp, url_prefix="/verify")
