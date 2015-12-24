from manage import *
import query

class QueryHandler(AdminBaseHandler):

    def get(self):
        self._serve_page()

    def post(self):
        self._serve_page()

    def _serve_page(self, error=None):
        querystring = self.request.get('querystring')
        try:
            results = query.run_gql(querystring)
        except Exception as e:
            results = []
            error = e

        template_values = {
            'querystring': querystring,
            'query_results': results,
            'error': error
        }
        self.render_template('admin-run_query.html', template_values)
