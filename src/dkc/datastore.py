from google.cloud import ndb

client = ndb.Client()

def g_ndb_wsgi_middleware(wsgi_app):
    def middleware(environ, start_response):
        with client.context():
            return wsgi_app(environ, start_response)
    return middleware
