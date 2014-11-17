from manage import *
from dkc.models import User
from google.appengine.ext import ndb

class OverviewHandler(AdminBaseHandler):

    def get(self):
        applicants = self.get_applicants()
        applications_keys = [a.application for a in applicants]
        applications = ndb.get_multi(applications_keys)
        template_values = {
            'applicants': applicants,
            'applications': applications,
            'admin_url': '/admin/overview'
        }
        self.render_template('admin-overview.html', template_values)
