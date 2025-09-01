from typing import Any, Dict
import json
import logging
from flask import Blueprint, request
from dkc.application_verification.bounce import on_verification_bounce_event
from common.email_provider import MailerSendMessageId

webhooks_bp = Blueprint("webhooks", __name__)

logger = logging.getLogger(__name__)


@webhooks_bp.route("/mailersend/event", methods=["POST"])
def mailersend_event():
    email_event = json.loads(request.data)
    if "type" not in email_event:
        logger.error("Received MailerSend event with no type: %s", email_event)
        return
    if (
        email_event["type"] == "activity.soft_bounced"
        or email_event["type"] == "activity.hard_bounced"
    ):
        handle_mailersend_bounced_event(email_event)
    else:
        logger.error("Received unrecognized MailerSend event: %s", email_event)
    return "ok"


def handle_mailersend_bounced_event(email_event: Dict[str, Any]):
    email_metadata = email_event["data"]["email"]
    message_id_mapping = MailerSendMessageId.find_by_message_id(
        email_metadata["message"]["id"]
    )
    on_verification_bounce_event(
        recipient=email_metadata["recipient"]["email"],
        dkc_application_key=message_id_mapping.dkc_application_key
    )
