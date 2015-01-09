from dkc.timezone import UTC, Eastern
from manage import *
from models import *
from datetime import datetime, timedelta

class SettingsHandler(AdminBaseHandler):

    def get(self):
        self._serve_page()
        
    def post(self):
        config = ndb.Key(Settings, 'config').get()
        if not config:
            config = Settings(id='config')

        config.secret_key = self.request.get('secret_key')

        early_due_date = self.request.get('early_due_date')
        try:
            early_due_date = datetime.strptime(early_due_date, "%B %d, %Y - %I:%M %p")
            early_due_date += timedelta(hours=5) # Eastern TZ offset
            config.early_due_date = early_due_date
        except:
            config.early_due_date = "Please put in a valid date (ex. February 1, 2015 - 11:59 PM)"
        due_date = self.request.get('due_date')
        try:
            due_date = datetime.strptime(due_date, "%B %d, %Y - %I:%M %p")
            due_date += timedelta(hours=5) # Eastern TZ offset
            config.due_date = due_date
        except:
            config.due_date = "Please put in a valid date (ex. February 14, 2015 - 11:59 PM)"

        config.sendgrid_username = self.request.get('sendgrid_username')
        config.sendgrid_password = self.request.get('sendgrid_password')

        config.put()
        self._serve_page()

    def _serve_page(self):
        config_key = ndb.Key(Settings, 'config')
        if config_key:
            config = config_key.get()
        else:
            config = {}

        template_values = {
            'config': config
        }
        self.render_template('admin-settings.html', template_values)
