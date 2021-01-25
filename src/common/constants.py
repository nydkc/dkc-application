import os
from datetime import datetime
from google.cloud import ndb
from common.datastore import db
from common.models import Settings

with db.context():
    config = ndb.Key(Settings, "config").get()
    if not config:
        config = Settings(id="config")

    ### Configuration options that REQUIRE a restart. ###

    SECRET_KEY = "Generate a secret key using /tools/generate_secret_key.py"
    try:
        SECRET_KEY = config.secret_key
    except:
        config.secret_key = SECRET_KEY

    # Used to protect login/register pages from spam
    RECAPTCHA_SECRET = "Get a secret key at https://www.google.com/recaptcha/admin"
    RECAPTCHA_SITE_KEY = "Get a site key at https://www.google.com/recaptcha/admin"
    try:
        RECAPTCHA_SECRET = config.recaptcha_secret
        RECAPTCHA_SITE_KEY = config.recaptcha_site_key
    except:
        config.recaptcha_secret = RECAPTCHA_SECRET
        config.recaptcha_site_key = RECAPTCHA_SITE_KEY

    GOOGLE_OAUTH_CLIENT_ID = "Get a client ID at https://console.developers.google.com/apis/credentials"
    GOOGLE_OAUTH_CLIENT_SECRET = "Get a client secret at https://console.developers.google.com/apis/credentials"
    try:
        GOOGLE_OAUTH_CLIENT_ID = config.google_oauth_client_id
        GOOGLE_OAUTH_CLIENT_SECRET = config.google_oauth_client_secret
    except:
        config.google_oauth_client_id = GOOGLE_OAUTH_CLIENT_ID
        config.google_oauth_client_secret = GOOGLE_OAUTH_CLIENT_SECRET

    ### Configuration options that can be loaded WITHOUT a restart. ###

    # Specific due dates for applications
    _DUE_DATE = "February 16, 2018 - 04:59 AM"  # UTC Time (Subtract 5 to get US/Eastern)
    try:
        _DUE_DATE = config.due_date
    except:
        config.due_date = datetime.strptime(_DUE_DATE, "%B %d, %Y - %I:%M %p")

    # Used for bulk email sending
    _SENDGRID_USERNAME = "< Sendgrid Username >"
    _SENDGRID_PASSWORD = "< Sendgrid Password >"
    _SENDGRID_API_KEY = "Get an API key at https://app.sendgrid.com/settings/api_keys"
    try:
        _SENDGRID_USERNAME = config.sendgrid_username
        _SENDGRID_PASSWORD = config.sendgrid_password
        _SENDGRID_API_KEY = config.sendgrid_api_key
    except:
        config.sendgrid_username = _SENDGRID_USERNAME
        config.sendgrid_password = _SENDGRID_PASSWORD
        config.sendgrid_api_key = _SENDGRID_API_KEY

    # Used for application content uploads
    _GCS_BUCKET = "{}.appspot.com".format(os.environ.get("GOOGLE_CLOUD_PROJECT", "dkc-app"))
    try:
        _GCS_BUCKET = config.gcs_bucket
    except:
        config.gcs_bucket = _GCS_BUCKET

    config.put()
