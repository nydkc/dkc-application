import webapp2
import logging
from datetime import datetime, timedelta
from google.appengine.ext import ndb
from webapp2_extras.appengine.auth.models import UserToken

class AuthTokenCleanupHandler(webapp2.RequestHandler):
    def get(self):
        query = UserToken.query()
        query = query.filter(UserToken.updated < datetime.now() - timedelta(days=14))
        auth_token_keys = map(lambda t: t.key, query.fetch())
        ndb.delete_multi(auth_token_keys)
        logging.info("Cleaned up %d auth tokens" % len(auth_token_keys))

application = webapp2.WSGIApplication([
    ('/cron/auth_token_cleanup', AuthTokenCleanupHandler)
], debug=True)
