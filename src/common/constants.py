from google.cloud import ndb
from common.datastore import db
from common.models import Settings

### Constants that are not stored in Datastore ###

# The number of days that an Auth Token is valid for.
# Used for application verification and forgot password link expiration.
AUTH_TOKEN_VALIDITY_DAYS = 14


with db.context():
    config: Settings = ndb.Key(Settings, "config").get()
    if not config:
        config = Settings(id="config")
        config.put()

### Configuration options that REQUIRE a restart. ###
### Other configuration options should be accessed via ndb Settings retrieval instead. ###

SECRET_KEY = config.secret_key
RECAPTCHA_SECRET = config.recaptcha_secret
RECAPTCHA_SITE_KEY = config.recaptcha_site_key
GOOGLE_OAUTH_CLIENT_ID = config.google_oauth_client_id
GOOGLE_OAUTH_CLIENT_SECRET = config.google_oauth_client_secret
