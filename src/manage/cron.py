import logging
from datetime import datetime, timedelta
from flask import abort, Blueprint, request
from google.cloud import ndb
from common.constants import AUTH_TOKEN_VALIDITY_DAYS
from dkc.auth.models import AuthToken

cron_bp = Blueprint("manage.cron", __name__)

APPENGINE_CRON_HEADER = "X-Appengine-Cron"


@cron_bp.route("/cron/auth_token_cleanup")
def auth_token_cleanup():
    if not request.headers.get(APPENGINE_CRON_HEADER, default=False):
        return abort(403)

    expired_tokens_query = AuthToken.query().filter(
        AuthToken.created < datetime.now() - timedelta(days=AUTH_TOKEN_VALIDITY_DAYS)
    )
    auth_token_keys = [t.key for t in expired_tokens_query.fetch()]
    ndb.delete_multi(auth_token_keys)
    logging.info("Cleaned up %d auth tokens", len(auth_token_keys))
    return "ok"
