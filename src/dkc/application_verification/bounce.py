import logging
from google.cloud import ndb


logger = logging.getLogger(__name__)


def bounced_message(email: str):
    return "FAILED TO SEND EMAIL TO: {}".format(email)


def on_verification_bounce_event(recipient: str, dkc_application_key: str):
    application = ndb.Key(urlsafe=dkc_application_key).get()
    applicant = application.key.parent().get()
    has_matching_recipient = False

    if recipient == application.verification_ltg_email:
        application.verification_ltg_sent = False
        application.verification_ltg_email = bounced_message(recipient)
        has_matching_recipient = True
    if recipient == application.verification_club_president_email:
        application.verification_club_president_sent = False
        application.verification_club_president_email = bounced_message(recipient)
        has_matching_recipient = True
    if recipient == application.verification_faculty_advisor_email:
        application.verification_faculty_advisor_sent = False
        application.verification_faculty_advisor_email = bounced_message(recipient)
        has_matching_recipient = True

    if not has_matching_recipient:
        logger.warning(
            "Could not match failed send event to recipient %s under user %s",
            recipient,
            applicant.email,
        )
        return

    application.put()

    logger.info(
        "Marked failure sending verification email to recipient %s under user %s",
        recipient,
        applicant.email,
    )
