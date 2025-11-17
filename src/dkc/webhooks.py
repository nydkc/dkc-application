from typing import Any, Dict
import json
import logging
from flask import Blueprint, request
from common.email_provider import EmailProviderMessageMapping
from dkc.application_verification.bounce import on_verification_bounce_event

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
    message_id_mapping = EmailProviderMessageMapping.find_by_message_id(
        provider_name="MailerSend", message_id=email_metadata["message"]["id"]
    )
    on_verification_bounce_event(
        recipient=email_metadata["recipient"]["email"],
        dkc_application_key=message_id_mapping.dkc_application_key,
    )


@webhooks_bp.route("/maileroo/event", methods=["POST"])
def maileroo_event():
    email_event = json.loads(request.data)
    if "event_type" not in email_event:
        logger.error(
            "Received Maileroo event with no event_type field: %s", email_event
        )
        return
    if email_event["event_type"] == "failed" or email_event["event_type"] == "deferred":
        handle_maileroo_bounced_event(email_event)
    else:
        logger.error("Received unrecognized Maileroo event: %s", email_event)
    return "ok"


def handle_maileroo_bounced_event(email_event: Dict[str, Any]):
    recipient_email = email_event["event_data"]["to"]
    reference_id = email_event["message_reference_id"]
    message_id_mapping = EmailProviderMessageMapping.find_by_message_id(
        provider_name="Maileroo", message_id=reference_id
    )
    on_verification_bounce_event(
        recipient=recipient_email,
        dkc_application_key=message_id_mapping.dkc_application_key,
    )
