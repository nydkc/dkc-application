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
