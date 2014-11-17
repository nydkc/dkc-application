from manage import *
from dkc.models import User

class OverviewHandler(AdminBaseHandler):

    def get(self):
        applicants = self.get_applicants()
        applications = [a.application.get() for a in applicants]
        template_values = {
            'applicants': applicants,
            'applications': applications,
            'admin_url': '/admin/overview'
        }
        self.render_template('admin-overview.html', template_values)
