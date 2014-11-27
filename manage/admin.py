from manage import *
from dkc.models import User
import query

class OverviewHandler(AdminBaseHandler):

    def get(self):
        applicants = query.get_all_applicants()
        applications = query.get_all_applications(applicants)
        template_values = {
            'applicants': applicants,
            'applications': applications,
            'admin_url': '/admin/overview'
        }
        self.render_template('admin-overview.html', template_values)
