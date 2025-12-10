import pytest
from common.models import Settings


@pytest.fixture
def settings(ndb_context):
    return Settings.get_config()
