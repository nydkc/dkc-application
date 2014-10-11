import os, webapp2, jinja2, cgi
from dkc import *

class TestHandler(BaseHandler):

    def get(self):
        self.response.out.write("<table><tbody>")

        for name in os.environ.keys():
            self.response.out.write("<tr><td>%s</td><td style='word-break:break-all'>%s</td></tr>" % (name, cgi.escape(str(os.environ[name]))))

        self.response.out.write("</tbody></table>")
