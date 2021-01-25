import os
from authlib.integrations.flask_client import OAuth


if os.getenv("GAE_ENV", "").startswith("standard"):
    # Production in the standard environment
    g_oauth = OAuth()
else:
    os.environ["AUTHLIB_INSECURE_TRANSPORT"] = "true"
    g_oauth = OAuth()

g_oauth.register(
    name="google",
    access_token_url="https://oauth2.googleapis.com/token",
    access_token_params=None,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    client_kwargs={
        "scope": "email",
        "access_type": "offline",
    },
)
