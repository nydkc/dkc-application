from admin.auth.views import auth_bp
from admin.cron import cron_bp
from admin.dashboard.views import dashboard_bp
from admin.env import env_bp
from admin.main_page.views import main_page_bp


def register_blueprints_to(app):
    app.register_blueprint(main_page_bp, url_prefix="/admin")
    app.register_blueprint(auth_bp, url_prefix="/admin")
    app.register_blueprint(dashboard_bp, url_prefix="/admin")
    app.register_blueprint(cron_bp)
    app.register_blueprint(env_bp, url_prefix="/admin")
