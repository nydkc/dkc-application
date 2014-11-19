from manage import *
import query

class ListsHandler(AdminBaseHandler):

    def get(self):
        emails = query.get_all_emails()
        template_values = {
            'emails': emails,
            'admin_url': '/admin/lists'
        }
        self.render_template('admin-lists.html', template_values)
