import os
import pytest

# Force Datastore Emulator
os.environ["DATASTORE_EMULATOR_HOST"] = "localhost:8500"
os.environ["DATASTORE_PROJECT_ID"] = "nydkc-test"
os.environ["GAE_ENV"] = "local"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
    os.path.dirname(__file__), "dummy_credentials.json"
)

pytest_plugins = [
    "tests.fixtures.core",
    "tests.fixtures.auth",
    "tests.fixtures.data",
    "tests.fixtures.email",
]

@pytest.fixture(autouse=True)
def mock_settings():
    """Mocks common.models.Settings.get_config to return a dummy config."""
    from unittest.mock import MagicMock, patch
    from common.models import Settings
    from datetime import datetime

    mock_config = MagicMock(spec=Settings)
    mock_config.due_date = datetime(2099, 1, 1)
    mock_config.awards_booklet_url = "http://example.com"

    with patch("common.models.Settings.get_config", return_value=mock_config):
        yield mock_config
