import logging
from google.cloud import ndb


def bounced_message(email):
    return "FAILED TO SEND EMAIL TO: {}".format(email)


def on_verification_bounce_event(email_event):
    assert email_event["dkc_purpose"] == "verification"
    if "dkc_application_key" not in email_event:
        logging.error("No application key in bounced email: %s", email_event)
        return

    application = ndb.Key(
        urlsafe=email_event["dkc_application_key"].encode("utf-8")
    ).get()
    applicant = application.key.parent().get()
    email_sent_to = email_event["email"]

    if email_sent_to == application.verification_ltg_email:
        application.verification_ltg_sent = False
        application.verification_ltg_email = bounced_message(email_sent_to)
    if email_sent_to == application.verification_club_president_email:
        application.verification_club_president_sent = False
        application.verification_club_president_email = bounced_message(email_sent_to)
    if email_sent_to == application.verification_faculty_advisor_email:
        application.verification_faculty_advisor_sent = False
        application.verification_faculty_advisor_email = bounced_message(email_sent_to)
    else:
        logging.warning(
            "Could not match failed send event to %s under user %s",
            email_sent_to,
            applicant.email,
        )
        return

    application.put()

    logging.error(
        "Marked failure sending verification email to %s under user %s",
        email_sent_to,
        applicant.email,
    )
