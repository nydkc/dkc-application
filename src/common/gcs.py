import os
import google.auth.credentials
from google.oauth2 import service_account
from google.cloud import storage

if os.getenv("GAE_ENV", "").startswith("standard"):
    # Production in the standard environment
    gcs = storage.Client()
else:
    # Local execution.
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        raise EnvironmentError(
            """===== ENVIRONMENT ERROR =====
Please set GOOGLE_APPLICATION_CREDENTIALS to the path of your service account credential file.
This is usually a JSON file with a key to a service account, following instructions from
https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys.
The preferred service account is the AppEngine service account:
    {}@appspot.gserviceaccount.com
===== ENVIORNMENT ERROR =====""".format(
                os.environ.get("GOOGLE_CLOUD_PROJECT", "dkc-app")
            )
        )
    gcs = storage.Client()
