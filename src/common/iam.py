import os
from google.cloud import resourcemanager_v3
from google.iam.v1 import iam_policy_pb2
from common.gcp import GCP_PROJECT_ID

if os.getenv("GAE_ENV", "").startswith("standard"):
    # Production in the standard environment
    cloudresourcemanager = resourcemanager_v3.ProjectsClient()
else:
    # Local execution.
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        raise EnvironmentError(
            f"""===== ENVIRONMENT ERROR =====
Please set GOOGLE_APPLICATION_CREDENTIALS to the path of your service account credential file.
This is usually a JSON file with a key to a service account, following instructions from
https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys.
The preferred service account is the AppEngine service account:
    {GCP_PROJECT_ID}@appspot.gserviceaccount.com
===== ENVIORNMENT ERROR ====="""
        )
    cloudresourcemanager = resourcemanager_v3.ProjectsClient()


def get_project_iam_policy():
    request = iam_policy_pb2.GetIamPolicyRequest(
        resource=f"projects/{GCP_PROJECT_ID}",
    )
    resp = cloudresourcemanager.get_iam_policy(request=request)
    return resp
