import os
from authlib.integrations.flask_client import OAuth


if os.getenv("GAE_ENV", "").startswith("standard"):
    # Production in the standard environment
    g_oauth = OAuth()
else:
    g_oauth = OAuth()

g_oauth.register(
    name="google",
    access_token_url="https://oauth2.googleapis.com/token",
    access_token_params=None,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params={
        "access_type": "offline",
        "prompt": "consent",
    },
    client_kwargs={
        "scope": "profile email",
    },
)


def refresh_oauth_token(token):
    if token.provider == "google":
        oauth2_session = g_oauth.google._get_oauth_client()
        new_token = oauth2_session.refresh_token(
            g_oauth.google.access_token_url, refresh_token=token.refresh_token
        )
        assert token.refresh_token == new_token["refresh_token"]
        token.access_token = new_token["access_token"]
        token.expires_at = new_token["expires_at"]
    else:
        raise NotImplementedError(
            "Cannot refresh token with provider: {}".format(token.provider)
        )
