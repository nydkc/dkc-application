from dkc.manage import *
from dkc.models import User

class AdminOverviewHandler(AdminBaseHandler):

    def get(self):
        query = User.query()
        applicants = query.fetch()
        template_values = {
            'applicants': applicants
        }
        self.render_template('admin-overview.html', template_values)

class AdminSearchHandler(AdminBaseHandler):

    def get(self):
        search = self.request.get('q')
# IMPLEMENT SEARCH FUNCTION
        self.render_template('admin-search.html')
