from dkc.main_page.views import main_page_bp
from dkc.auth.views import auth_bp
from dkc.application.views import application_bp
from dkc.application_verification.views import application_verification_bp
from dkc.dummy.views import dummy_bp
from dkc.webhooks import webhooks_bp


def register_blueprints_to(app):
    app.register_blueprint(main_page_bp)
    app.register_blueprint(webhooks_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(application_bp, url_prefix="/application")
    app.register_blueprint(application_verification_bp, url_prefix="/verify")
    app.register_blueprint(dummy_bp, url_prefix="/dummy")
