import pytest
import os
import sys
from common.datastore import db
from main import app as flask_app
import bcrypt

# Patch bcrypt for passlib compatibility
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type("about", (object,), {"__version__": bcrypt.__version__})


@pytest.fixture
def app():
    flask_app.config.update(
        {
            "TESTING": True,
            "SECRET_KEY": "test_secret_key",
            "WTF_CSRF_ENABLED": False,
        }
    )

    # Mock ndb.Client.context to be reentrant.
    # This prevents "Context is already created" errors when the middleware tries to
    # create a context inside the one already provided by the `ndb_context` fixture.

    from google.cloud import ndb
    import contextlib

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
    return app.test_client()


@pytest.fixture(autouse=True)
def ndb_context():
    # Use the same client as the app to avoid context conflicts
    with db.context():
        yield
