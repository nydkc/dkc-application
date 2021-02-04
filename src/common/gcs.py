import os
import google.auth
from google.auth import compute_engine
from google.cloud import storage
from .constants import _GCS_BUCKET

if os.getenv("GAE_ENV", "").startswith("standard"):
    # Production in the standard environment
    gcs = storage.Client()
    # Attempt an access to GCS to "initialize" the client credentials for use by the signer later.
    gcs.lookup_bucket
    gcs.get_bucket(_GCS_BUCKET)
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


def generate_signed_url_for(blob: storage.Blob, **kwargs):
    if os.getenv("GAE_ENV", "").startswith("standard"):
        # Production in the standard environment
        return cloud_iam_sign_blob(blob, **kwargs)
    else:
        # Local execution.
        return blob.generate_signed_url(**kwargs)


def cloud_iam_sign_blob(blob: storage.Blob, **kwargs):
    """Use the default AppEngine service account to sign the blob using Cloud IAM."""
    if "credentials" in kwargs:
        del kwargs["credentials"]
    auth_request = google.auth.transport.requests.Request()
    # Use a credential that uses Cloud IAM's Sign Blob API for signing.
    signing_credentials = compute_engine.IDTokenCredentials(
        auth_request, "", service_account_email=gcs._credentials.service_account_email
    )
    return blob.generate_signed_url(credentials=signing_credentials, **kwargs)
