import json
import logging
from flask import Blueprint, request
from dkc.verify.bounce import on_verification_bounce_event

webhooks_bp = Blueprint("webhooks", __name__)

logger = logging.getLogger(__name__)


@webhooks_bp.route("/sendgrid/event", methods=["POST"])
def sendgrid_event():
    email_events = json.loads(request.data)
    for email_event in email_events:
        if email_event["event"] == "bounce" or email_event["event"] == "dropped":
            handle_bounced_event(email_event)
        else:
            logger.error("Received unrecognized Sendgrid event: %s", email_event)
    return "ok"


def handle_bounced_event(email_event):
    if "dkc_purpose" not in email_event:
        logger.error("Received Sengrid event with no purpose: %s", email_event)
        return

    if email_event["dkc_purpose"] == "verification":
        on_verification_bounce_event(email_event)
    else:
        logger.error(
            "Received Sendgrid event with unrecognized purpose: %s", email_event
        )
