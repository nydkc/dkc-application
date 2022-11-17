import logging
import time
from datetime import datetime, timedelta
from flask import abort, Blueprint, request
from google.cloud import ndb
from common.constants import AUTH_TOKEN_VALIDITY_DAYS
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
