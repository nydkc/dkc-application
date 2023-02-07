from typing import Any, Dict
import json
import logging
from flask import Blueprint, request
from dkc.application_verification.bounce import on_verification_bounce_event
from common.email_provider import MailerSendMessageId

webhooks_bp = Blueprint("webhooks", __name__)

logger = logging.getLogger(__name__)


@webhooks_bp.route("/sendgrid/event", methods=["POST"])
def sendgrid_event():
    email_events = json.loads(request.data)
    for email_event in email_events:
        if email_event["event"] == "bounce" or email_event["event"] == "dropped":
            handle_sendgrid_bounced_event(email_event)
        else:
            logger.error("Received unrecognized SendGrid event: %s", email_event)
    return "ok"


def handle_sendgrid_bounced_event(email_event: Dict[str, Any]):
    if "dkc_purpose" not in email_event:
        logger.error("Received SendGrid event with no purpose: %s", email_event)
        return

    if email_event["dkc_purpose"] != "verification":
        logger.error(
            "Received SendGrid event with unrecognized purpose: %s", email_event
        )
        return

    if "dkc_application_key" not in email_event:
        logger.error(
            "No application key in bounced verification email: %s", email_event
        )
        return

    on_verification_bounce_event(
        recipient=email_event["email"],
        dkc_application_key=email_event["dkc_application_key"].encode("utf-8"),
    )


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
