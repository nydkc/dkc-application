import pytest
from common.models import Settings


@pytest.fixture
def settings(ndb_context):
    """Provides a Settings configuration object for tests."""
    return Settings.get_config()
