import os
from flask import request
from flask_talisman import Talisman


class TalismanWithCronHttpsBypass(Talisman):
    def _force_https(self):
        """
        Override the default _force_https to handle GAE cron request, which
        uses HTTP and treats the HTTPS 302 redirect as a failure.
        """
        if request.path.startswith("/cron"):
            return
        return super()._force_https()


def g_flask_talisman_init_app(app):
    TalismanWithCronHttpsBypass(app, force_https=True, content_security_policy=None)
