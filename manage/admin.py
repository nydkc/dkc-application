from manage import *
from dkc.models import User
import query

class OverviewHandler(AdminBaseHandler):

    def get(self):
        applicants = query.get_all_applicants()
        applications = query.get_all_applications()
        pairs = zip(applicants, applications)
        pairs.sort(key=lambda pair: (pair[0].division, pair[0].first_name, pair[0].last_name))
        template_values = {
            'pairs': pairs,
            'admin_url': '/admin/overview'
        }
        self.render_template('admin-overview.html', template_values)
