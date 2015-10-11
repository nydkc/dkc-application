import time
from manage import *
from dkc.models import User
import query

class SearchHandler(AdminBaseHandler):

    def get(self):
        search = self.request.get('q')
        applicants = query.get_all_applicants()
        results = []

        start = time.time()
        for applicant in applicants:
            if self.match(applicant, search):
                results.append(applicant)
        elapsed = time.time() - start

        template_values = {
            'q': search,
            'elapsed': elapsed,
            'applicants': results,
            'admin_url': '/admin/search'
        }
        self.render_template('admin-search.html', template_values)

    def match(self, applicant, search):
        applicant_info = [applicant.first_name, applicant.last_name, applicant.email, applicant.grade, applicant.address, applicant.city, applicant.zip_code, applicant.phone_number, applicant.division, applicant.ltg, applicant.school, applicant.school_address, applicant.school_city, applicant.school_zip_code, applicant.club_president, applicant.club_president_phone_number, applicant.faculty_advisor, applicant.faculty_advisor_phone_number]
        return search.lower() in "###".join(map(str, applicant_info)).lower()
