import os, webapp2, jinja2, cgi
from dkc import *
from pdf import generate_pdf

class TestHandler(BaseHandler):

    def get(self):
        result = []
        result.append("<table><tbody>")

        for name in os.environ.keys():
            result.append("<tr><td>%s</td><td style='word-break:break-all'>%s</td></tr>" % (name, cgi.escape(str(os.environ[name]))))

        result.append("</tbody></table>")
        html = ''.join(result)

        self.response.headers['content-type'] = 'application/pdf'
        self.response.out.write(generate_pdf(html))
