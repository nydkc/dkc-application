import logging
import time
from datetime import datetime, timedelta
from flask import abort, Blueprint, request
from google.cloud import ndb
from common.constants import AUTH_TOKEN_VALIDITY_DAYS
from common.email_provider import (
    MailerSend,
    MailerSendMessageId,
    Email,
    Subject,
    HtmlContent,
    CustomArgs,
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


@cron_bp.route("/cron/auth_token_cleanup")
def auth_token_cleanup():
    if not request.headers.get(APPENGINE_CRON_HEADER, default=False):
        return abort(403)

    expired_tokens_query = AuthToken.query().filter(
        AuthToken.created < datetime.now() - timedelta(days=AUTH_TOKEN_VALIDITY_DAYS)
    )
    auth_token_keys = [tkey for tkey in expired_tokens_query.fetch(keys_only=True)]
    ndb.delete_multi(auth_token_keys)
    logger.info("Cleaned up %d auth tokens", len(auth_token_keys))
    return "ok"


@cron_bp.route("/cron/admin_user_token_cleanup")
def admin_user_token_cleanup():
    if not request.headers.get(APPENGINE_CRON_HEADER, default=False):
        return abort(403)

    expired_admin_user_tokens_query = AdminUser.query().filter(
        AdminUser.oauth2_token.expires_at < int(time.time())
    )
    admin_user_token_keys = [
        tkey for tkey in expired_admin_user_tokens_query.fetch(keys_only=True)
    ]
    ndb.delete_multi(admin_user_token_keys)
    logger.info("Cleaned up %d admin user tokens", len(admin_user_token_keys))
    return "ok"


@cron_bp.route("/cron/mailersend_message_id_cleanup")
def mailersend_message_id_cleanup():
    if not request.headers.get(APPENGINE_CRON_HEADER, default=False):
        return abort(403)

    # Mappings do not need to be stored for long, since it is used almost
    # immediately by bounced email webhook
    expired_message_id_query = MailerSendMessageId.query().filter(
        MailerSendMessageId.timestamp < datetime.now() - timedelta(days=1)
    )
    message_id_keys = [key for key in expired_message_id_query.fetch(keys_only=True)]
    ndb.delete_multi(message_id_keys)
    logger.info("Cleaned up %d message id mappings", len(message_id_keys))
    return "ok"


@cron_bp.route("/cron/mailersend_heartbeat")
def mailersend_heartbeat():
    if not request.headers.get(APPENGINE_CRON_HEADER, default=False):
        return abort(403)

    settings = ndb.Key(Settings, "config").get()
    ms = MailerSend(api_key=settings.mailersend_api_key)
    response = ms.send_email(
        from_email=Email(email="dkc-app@nydkc.org", name="NYDKC DKC Application"),
        to_email=Email(email="dkc-app@nydkc.org"),
        subject=Subject(line="DKC Application is still alive!"),
        html_content=HtmlContent(
            content="Hello! This email keeps the MailerSend account active."
        ),
        custom_args=CustomArgs(
            metadata=(
                {
                    "dkc_purpose": "heartbeat",
                }
            )
        ),
    )
    if response.http_code != 202:
        logger.error("Error sending heartbeat email: %s", response.errors)
        return abort(503)
    return "ok"
