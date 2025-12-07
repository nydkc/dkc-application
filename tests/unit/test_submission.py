import pytest
from dkc.application.models import Application
from google.cloud import ndb
import datetime


def test_application_submission_timestamp(ndb_context):
    app = Application()
    app.submit_time = datetime.datetime.utcnow()
    app.put()

    fetched_app = app.key.get()
    assert fetched_app.submit_time is not None
    assert isinstance(fetched_app.submit_time, datetime.datetime)


def test_application_graded_status(ndb_context):
    app = Application()
    app.graded = False
    app.put()

    fetched_app = app.key.get()
    assert fetched_app.graded is False

    app.graded = True
    app.put()

    fetched_app = app.key.get()
    assert fetched_app.graded is True
