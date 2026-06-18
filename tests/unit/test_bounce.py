import pytest
from unittest.mock import MagicMock, patch
from dkc.application_verification.bounce import (
    bounced_message,
    on_verification_bounce_event,
)
from dkc.application.models import Application
from dkc.auth.models import User


def test_bounced_message_formatting():
    email = "test@example.com"
    expected = "FAILED TO SEND EMAIL TO: test@example.com"
    assert bounced_message(email) == expected


def test_on_verification_bounce_event_ltg(ndb_context):
    user = User(email="applicant@example.com")
    user_key = user.put()

    app = Application(parent=user_key)
    app.verification_ltg_email = "ltg@example.com"
    app.verification_ltg_sent = True
    app_key = app.put()

    on_verification_bounce_event("ltg@example.com", app_key.urlsafe().decode("utf-8"))

    updated_app = app_key.get()
    assert updated_app.verification_ltg_sent is False
    assert (
        "FAILED TO SEND EMAIL TO: ltg@example.com" == updated_app.verification_ltg_email
    )


def test_on_verification_bounce_event_president(ndb_context):
    user = User(email="applicant@example.com")
    user_key = user.put()

    app = Application(parent=user_key)
    app.verification_club_president_email = "pres@example.com"
    app.verification_club_president_sent = True
    app_key = app.put()

    on_verification_bounce_event("pres@example.com", app_key.urlsafe().decode("utf-8"))

    updated_app = app_key.get()
    assert updated_app.verification_club_president_sent is False
    assert (
        "FAILED TO SEND EMAIL TO: pres@example.com"
        == updated_app.verification_club_president_email
    )


def test_on_verification_bounce_event_advisor(ndb_context):
    user = User(email="applicant@example.com")
    user_key = user.put()

    app = Application(parent=user_key)
    app.verification_faculty_advisor_email = "advisor@example.com"
    app.verification_faculty_advisor_sent = True
    app_key = app.put()

    on_verification_bounce_event(
        "advisor@example.com", app_key.urlsafe().decode("utf-8")
    )

    updated_app = app_key.get()
    assert updated_app.verification_faculty_advisor_sent is False
    assert (
        "FAILED TO SEND EMAIL TO: advisor@example.com"
        == updated_app.verification_faculty_advisor_email
    )


def test_on_verification_bounce_event_no_match(ndb_context, caplog):
    user = User(email="applicant@example.com")
    user_key = user.put()

    app = Application(parent=user_key)
    app.verification_ltg_email = "ltg@example.com"
    app_key = app.put()

    with caplog.at_level("WARNING"):
        on_verification_bounce_event(
            "unknown@example.com", app_key.urlsafe().decode("utf-8")
        )

    assert (
        "Could not match failed send event to recipient unknown@example.com"
        in caplog.text
    )

    updated_app = app_key.get()
    assert updated_app.verification_ltg_email == "ltg@example.com"
