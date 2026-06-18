import pytest
from dkc.auth.models import AuthToken
from dkc.application.models import Application
from google.cloud import ndb
import datetime


def test_auth_token_creation(ndb_context):
    token = AuthToken(type="verification")
    token.put()
    assert token.created is not None
    assert token.type == "verification"


def test_application_verification_fields(ndb_context):
    app = Application()
    app.verification_ltg = False
    app.verification_ltg_sent = False
    app.put()

    fetched_app = app.key.get()
    assert fetched_app.verification_ltg is False
    assert fetched_app.verification_ltg_sent is False
