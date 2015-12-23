from google.appengine.ext import ndb
from datetime import datetime
from manage.models import Settings

config = ndb.Key(Settings, 'config').get()
if not config:
    config = Settings(id='config')

SECRET_KEY = 'Generate a secret key using /generate_secret_key.py'
try:
    SECRET_KEY = config.secret_key
except:
    config.secret_key = SECRET_KEY
PASSWORD_SECRET_KEY = config.secret_key

# Specific due dates for applications (early, regular)
EARLY_DUE_DATE = "February 2, 2015 - 04:59 AM" # UTC Time (Subtract 5 to get US/Eastern)
try:
    APPLICATION_DUE_DATE = config.early_due_date 
except:
    config.early_due_date = datetime.strptime(EARLY_DUE_DATE, "%B %d, %Y - %I:%M %p")
APPLICATION_EARLY_DUE_DATE = config.early_due_date 

DUE_DATE = "February 16, 2015 - 04:59 AM" # UTC Time
try:
    APPLICATION_DUE_DATE = config.due_date 
except:
    config.due_date = datetime.strptime(DUE_DATE, "%B %d, %Y - %I:%M %p")
APPLICATION_DUE_DATE = config.due_date 

# Used for bulk email sending
SENDGRID_USERNAME = "< Sendgrid Username >"
SENDGRID_PASSWORD = "< Sendgrid Password >"
try:
    SENDGRID_USERNAME = config.sendgrid_username
    SENDGRID_PASSWORD = config.sendgrid_password
except:
    config.sendgrid_username = SENDGRID_USERNAME
    config.sendgrid_password = SENDGRID_PASSWORD
SENDGRID_USERNAME = config.sendgrid_username
SENDGRID_PASSWORD = config.sendgrid_password

RECAPTCHA_SECRET = "Go to https://www.google.com/recaptcha/admin to create a recaptcha secret key"
try:
    RECAPTCHA_SECRET = config.recaptcha_secret
except:
    config.recaptcha_secret = RECAPTCHA_SECRET
RECAPTCHA_SECRET = config.recaptcha_secret

config.put()
