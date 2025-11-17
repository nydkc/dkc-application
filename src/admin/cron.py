import logging
import time
from datetime import datetime, timedelta
from flask import abort, Blueprint, request
from google.cloud import ndb
from common.constants import AUTH_TOKEN_VALIDITY_DAYS
from common.email_provider import (
    MailerSend,
    Maileroo,
    EmailProviderMessageMapping,
)
from common.models import Settings
from dkc.auth.models import AuthToken
from admin.auth.models import AdminUser

cron_bp = Blueprint("admin_cron", __name__)

logger = logging.getLogger(__name__)

# A special header that is attached to App Engine cron requests. This header is
# set internally and cannot be set by clients.
# See https://cloud.google.com/appengine/docs/flexible/python/scheduling-jobs-with-cron-yaml#validating_cron_requests
APPENGINE_CRON_HEADER = "X-Appengine-Cron"


@cron_bp.before_request
def restrict_to_cron():
    if not request.headers.get(APPENGINE_CRON_HEADER, default=False):
        return abort(403)


@cron_bp.route("/cron/auth_token_cleanup")
def auth_token_cleanup():
    expired_tokens_query = AuthToken.query().filter(
        AuthToken.created < datetime.now() - timedelta(days=AUTH_TOKEN_VALIDITY_DAYS)
    )
    auth_token_keys = [tkey for tkey in expired_tokens_query.fetch(keys_only=True)]
    ndb.delete_multi(auth_token_keys)
    logger.info("Cleaned up %d auth tokens", len(auth_token_keys))
    return "ok"


@cron_bp.route("/cron/admin_user_token_cleanup")
def admin_user_token_cleanup():
    expired_admin_user_tokens_query = AdminUser.query().filter(
        AdminUser.oauth2_token.expires_at < int(time.time())
    )
    admin_user_token_keys = [
        tkey for tkey in expired_admin_user_tokens_query.fetch(keys_only=True)
    ]
    ndb.delete_multi(admin_user_token_keys)
    logger.info("Cleaned up %d admin user tokens", len(admin_user_token_keys))
    return "ok"


@cron_bp.route("/cron/email_message_id_cleanup")
def email_message_id_cleanup():
    # Mappings do not need to be stored for long, since it is used almost
    # immediately by bounced email webhook
    deleted_count = EmailProviderMessageMapping.delete_expired_mappings(days_old=1)
    logger.info("Cleaned up %d message id mappings", deleted_count)
    return "ok"


@cron_bp.route("/cron/mailersend_heartbeat")
def mailersend_heartbeat():
    settings = ndb.Key(Settings, "config").get()
    ms = MailerSend(api_key=settings.mailersend_api_key)
    response = ms.send_heartbeat_email()
    if not response.success:
        logger.error("Error sending heartbeat email: %s", response.errors)
        return abort(503)
    return "ok"


@cron_bp.route("/cron/maileroo_heartbeat")
def maileroo_heartbeat():
    settings = ndb.Key(Settings, "config").get()
    mr = Maileroo(api_key=settings.maileroo_api_key)
    response = mr.send_heartbeat_email()
    if not response.success:
        logger.error("Error sending heartbeat email: %s", response.errors)
        return abort(503)
    return "ok"
