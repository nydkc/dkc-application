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

        due_date = self.request.get('due_date')
        try:
            due_date = datetime.strptime(due_date, "%B %d, %Y - %I:%M %p")
            due_date += timedelta(hours=5) # Eastern TZ offset
            config.due_date = due_date
        except:
            config.due_date = "Please put in a valid date (ex. February 14, 2015 - 11:59 AM)"
        config.secret_key = self.request.get('secret_key')
        config.put()
        self._serve_page()

    def _serve_page(self):
        config_key = ndb.Key(Settings, 'config')
        if config_key:
            config = config_key.get()
            due_date = config.due_date if config else ''
            secret_key = config.secret_key if config else ''
        else:
            due_date = ''
            secret_key = ''
        template_values = {
            'due_date': due_date,
            'secret_key': secret_key
        }
        self.render_template('admin-settings.html', template_values)
