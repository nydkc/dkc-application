from manage import *
from models import *
import query

class OverviewHandler(AdminBaseHandler):

    def get(self):
        config = ndb.Key(Settings, 'config').get()
        if not config:
            config = Settings(id='config')
        due_date = config.due_date

        applicants, applications = query.get_all_overview()
        template_values = {
            'applicants': applicants,
            'applications': applications,
            'admin_url': '/admin/overview',
            'DUE_DATE': due_date
        }
        self.render_template('admin-overview.html', template_values)
