import contextlib
import pytest
from google.cloud import ndb
from common.datastore import db
from main import app as flask_app


@pytest.fixture
def app():
    """
    Provides a configured Flask app for testing.

    Configures the app with test settings and patches ndb.Client.context
    to be reentrant, preventing "Context is already created" errors.
    """
    flask_app.config.update(
        {
            "TESTING": True,
            "SECRET_KEY": "test_secret_key",
            "RECAPTCHA_PUBLIC_KEY": "test_recaptcha_public_key",
            "RECAPTCHA_PRIVATE_KEY": "test_recaptcha_private_key",
            "GOOGLE_CLIENT_ID": "test_google_client_id",
            "GOOGLE_CLIENT_SECRET": "test_google_client_secret",
            "WTF_CSRF_ENABLED": False,
        }
    )

    # Mock ndb.Client.context to be reentrant.
    # This prevents "Context is already created" errors when the middleware tries to
    # create a context inside the one already provided by the `ndb_context` fixture.
    original_context_method = ndb.Client.context

    def reentrant_context(self, *args, **kwargs):
        if ndb.context.get_context(raise_context_error=False):
            return contextlib.nullcontext()
        return original_context_method(self, *args, **kwargs)

    # Patch the method globally for the duration of the app fixture
    ndb.Client.context = reentrant_context

    yield flask_app

    # Teardown: restore original method
    ndb.Client.context = original_context_method


@pytest.fixture
def client(app):
    """Provides a Flask test client for making HTTP requests."""
    return app.test_client()


@pytest.fixture(autouse=True)
def ndb_context():
    """
    Establishes NDB datastore context for all tests.

    This fixture runs automatically for every test (autouse=True),
    ensuring the datastore context is available.
    """
    with db.context():
        yield
