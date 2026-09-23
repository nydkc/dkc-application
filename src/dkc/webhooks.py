from typing import Any, Dict, Optional, Tuple
import json
import logging
from flask import Blueprint, request
from common.email_provider import EmailProviderMessageMapping
from dkc.application_verification.bounce import on_verification_bounce_event

webhooks_bp = Blueprint("webhooks", __name__)

logger = logging.getLogger(__name__)


@webhooks_bp.route("/mailersend/event", methods=["POST"])
def mailersend_event():
    try:
        email_event = json.loads(request.data)
    except Exception as e:
        logger.error("Failed to parse MailerSend event JSON: %s", e)
        return "bad request", 400

    if "type" not in email_event:
        logger.error("Received MailerSend event with no type: %s", email_event)
        return "bad request", 400
    if (
        email_event["type"] == "activity.soft_bounced"
        or email_event["type"] == "activity.hard_bounced"
    ):
        handle_mailersend_bounced_event(email_event)
    elif email_event["type"] == "webhook.test":
        logger.info("Received MailerSend webhook test: %s", email_event)
    else:
        logger.error("Received unrecognized MailerSend event: %s", email_event)
    return "ok"


def _extract_mailersend_v2_info(
    data: Dict[str, Any],
) -> Tuple[Optional[str], Optional[str]]:
    """Extracts (message_id, recipient_email) from MailerSend Webhooks 2.0 payload format.

    MailerSend Webhooks 2.0 uses a streamlined, flattened JSON structure to reduce payload size
    and improve performance (https://www.mailersend.com/whats-new/webhooks-v2).

    Key differences from v1.0:
    - `message_id`: Directly available at `data.message_id` (in v1.0, nested in `data.email.message.id`).
    - `recipient`: Directly available at `data.recipient` as a string (in v1.0, nested in `data.email.recipient.email`).

    Example v2.0 payload:
    {
        "type": "activity.soft_bounced",
        "created_at": "2025-08-05T21:24:02.000000Z",
        "data": {
            "id": "6892766a5b66e2daf3dc9157",
            "domain_id": "yv69oxl5kl785kw2",
            "message_id": "6892766ae78995a317577aa1",
            "email_id": "6892766a8d52ba62543d5e71",
            "type": "soft_bounced",
            "recipient": "test@mailersend.com",
            "meta": {
                "bounce_reason": "Mailbox full",
                "bounce_code": 452,
                "bounce_type": "soft"
            }
        }
    }
    """
    message_id = data.get("message_id")
    recipient = data.get("recipient")
    recipient_email = (
        recipient.get("email") if isinstance(recipient, dict) else recipient
    )
    return message_id, recipient_email


def _extract_mailersend_v1_info(
    data: Dict[str, Any],
) -> Tuple[Optional[str], Optional[str]]:
    """Extracts (message_id, recipient_email) from MailerSend Webhooks 1.0 (legacy) format.

    In Webhooks 1.0:
    - `message_id`: Deeply nested in `data.email.message.id`.
    - `recipient`: Deeply nested in `data.email.recipient.email`.

    Example v1.0 payload:
    {
        "type": "activity.soft_bounced",
        "data": {
            "object": "activity",
            "id": "5fc0d006b42c3e16e1774882",
            "type": "soft_bounced",
            "email": {
                "message": {
                    "id": "5fc0d003f718c90162341852"
                },
                "recipient": {
                    "email": "test@mailersend.com"
                }
            }
        }
    }
    """
    email_metadata = data.get("email", {})
    message_id = email_metadata.get("message", {}).get("id")
    recipient = email_metadata.get("recipient")
    recipient_email = (
        recipient.get("email") if isinstance(recipient, dict) else recipient
    )
    return message_id, recipient_email


def extract_mailersend_bounce_metadata(
    email_event: Dict[str, Any],
) -> Tuple[Optional[str], Optional[str]]:
    """Extracts (message_id, recipient_email) by inspecting payload structure.

    Checks for Webhooks 2.0 structure (`data.message_id`) first, falling back to
    Webhooks 1.0 structure (`data.email`) if present.
    """
    data = email_event.get("data", {})
    if "message_id" in data:
        return _extract_mailersend_v2_info(data)
    elif "email" in data:
        return _extract_mailersend_v1_info(data)
    return None, None


def handle_mailersend_bounced_event(email_event: Dict[str, Any]):
    message_id, recipient_email = extract_mailersend_bounce_metadata(email_event)

    if not message_id or not recipient_email:
        logger.error(
            "MailerSend bounce event missing message_id or recipient: message_id=%s, recipient=%s, event=%s",
            message_id,
            recipient_email,
            email_event,
        )
        return

    message_id_mapping = EmailProviderMessageMapping.find_by_message_id(
        provider_name="MailerSend", message_id=message_id
    )
    if message_id_mapping is None:
        logger.error(
            "Did not find mapping for MailerSend message ID: %s",
            message_id,
        )
        return
    on_verification_bounce_event(
        recipient_email,
        message_id_mapping.dkc_application_key,
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
    if message_id_mapping is None:
        logger.error("Did not find mapping for Maileroo message ID: %s", reference_id)
        return
    on_verification_bounce_event(
        recipient_email,
        message_id_mapping.dkc_application_key,
    )
