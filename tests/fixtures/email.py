import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_email_provider():
    provider = MagicMock()
    response = MagicMock()
    response.success = True
    provider.send_email.return_value = response
    return provider
