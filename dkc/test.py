import os, webapp2, jinja2, cgi
from dkc import *
from download import generate_pdf

class TestHandler(BaseHandler):

    def get(self, resource):
        result = []
        result.append("<table><tbody>")

        for name in os.environ.keys():
            result.append("<tr><td>%s</td><td style='word-break:break-all'>%s</td></tr>" % (name, cgi.escape(str(os.environ[name]))))

        result.append("</tbody></table>")
        html = ''.join(result)

        if 'pdf' in str(resource):
            self.response.headers['content-type'] = 'application/pdf'
            self.response.out.write(generate_pdf(html))
        else:
            self.response.out.write(html)
