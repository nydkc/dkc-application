import pytest
from datetime import datetime
from google.cloud import ndb
from common.models import Settings


@pytest.fixture
def settings(ndb_context):
    s = Settings(
        key=ndb.Key(Settings, "config"),
        due_date=datetime.now(),
        gcs_bucket="test-bucket",
    )
    s.put()
    return s
