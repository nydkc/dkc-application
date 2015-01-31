from manage import *
from dkc.models import User
import query

class OverviewHandler(AdminBaseHandler):

    def get(self):
        applicants, applications = query.get_all_overview()
        template_values = {
            'applicants': applicants,
            'applications': applications,
            'admin_url': '/admin/overview'
        }
        self.render_template('admin-overview.html', template_values)
