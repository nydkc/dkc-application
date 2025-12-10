from __future__ import annotations
from datetime import datetime
from google.cloud import ndb
from common.gcp import GCP_PROJECT_ID


class Settings(ndb.Model):
    """
    Singleton model for configuration settings. Stored in GCP Datastore with key "config".
    """

    # For Flask security
    secret_key = ndb.StringProperty(
        default="Generate a secret key using /tools/generate_secret_key.py"
    )

    # For login bot protection
    recaptcha_site_key = ndb.StringProperty(
        default="Get a secret key at https://www.google.com/recaptcha/admin"
    )
    recaptcha_secret = ndb.StringProperty(
        default="Get a site key at https://www.google.com/recaptcha/admin"
    )

    # For Google OAuth login on admin pages
    google_oauth_client_id = ndb.StringProperty(
        default="Get a client ID at https://console.developers.google.com/apis/credentials"
    )
    google_oauth_client_secret = ndb.StringProperty(
        default="Get a client secret at https://console.developers.google.com/apis/credentials"
    )

    # For sending emails
    mailersend_api_key = ndb.StringProperty(
        default="Get an API key at https://app.mailersend.com/api-tokens"
    )
    maileroo_api_key = ndb.StringProperty(
        default="Get an API key at https://app.maileroo.com/applications"
    )

    # For storing any uploaded files
    gcs_bucket = ndb.StringProperty(default=f"{GCP_PROJECT_ID}.appspot.com")

    # DKC Application-specific settings
    due_date = ndb.DateTimeProperty(default=datetime.strptime("2015", "%Y"))
    awards_booklet_url = ndb.StringProperty()

    @classmethod
    def get_config(cls) -> Settings:
        """
        Lazily fetch and cache the Settings configuration from datastore.
        This is called on first access rather than at module import time,
        allowing tests to run without requiring the datastore emulator to be pre-started.
        """
        config: Settings = ndb.Key(cls, "config").get()
        if not config:
            config = cls(id="config")
            config.put()
        return config
