from manage import *
from dkc.models import User

class OverviewHandler(AdminBaseHandler):

    def get(self):
        applicants = self.get_applicants()
        template_values = {
            'applicants': applicants,
            'admin_url': '/admin/overview'
        }
        self.render_template('admin-overview.html', template_values)
