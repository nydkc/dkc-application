from manage import *
import query

class ListsHandler(AdminBaseHandler):

    def get(self):
        applicants = query.get_all_applicants()
        applications = query.get_all_applications()
        submitted_applicants = []
        not_submitted_applicants = []
        for index, applicant in enumerate(applicants):
            pair = (applicant, applications[index])
            if pair[1].submit_time:
                submitted_applicants.append(pair)
            else:
                not_submitted_applicants.append(pair)

        template_values = {
            'applicants': applicants,
            'applications': applications,
            'submitted_applicants': submitted_applicants,
            'not_submitted_applicants': not_submitted_applicants,
            'admin_url': '/admin/lists'
        }
        self.render_template('admin-lists.html', template_values)
