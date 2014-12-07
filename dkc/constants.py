from manage.models import *
from datetime import datetime
from google.appengine.ext import ndb

config = ndb.Key(Settings, 'config').get()
if not config:
    config = Settings(id='config')

# Generate one using /generate_secret_key.py
SECRET_KEY = 'HJ20pzoDQblIyj3ygyLIo9WObPLHPqXbhm2lXKsm1iY8T2TXkdQZP5ViCRBbfUPXrHE6LaZORHnxRIAQ6gDdxAnBWuSBMduqSJIc'
try:
    SECRET_KEY = config.secret_key
except:
    config.secret_key = SECRET_KEY
PASSWORD_SECRET_KEY = config.secret_key

DUE_DATE = "February 15, 2015 - 04:59 AM" # UTC Time
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

config.put()
