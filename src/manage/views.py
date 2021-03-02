from manage.admin_main_page.views import main_page_bp
from manage.admin_auth.views import auth_bp
from manage.admin.views import admin_bp
from manage.cron import cron_bp


def register_blueprints_to(app):
    app.register_blueprint(main_page_bp, url_prefix="/admin")
    app.register_blueprint(auth_bp, url_prefix="/admin")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(cron_bp)
