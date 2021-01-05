import html
import os
from flask import request, make_response, render_template
from dkc.util import generate_pdf
from . import dummy_bp


@dummy_bp.route("/env")
def env():
    table = []
    table.append("<table><tbody>")
    for key, value in os.environ.items():
        table.append(
            '<tr><td style="width:200px">%s</td><td style="word-break:break-all">%s</td></tr>'
            % (key, html.escape(value))
        )
    table.append("</tbody></table>")
    response_html = "".join(table)

    if request.args.get("media") == "pdf":
        response = make_response(generate_pdf(response_html))
        response.headers["content-type"] = "application/pdf"
        return response
    else:
        return response_html


# @dummy_bp.route('/verification_email')
# def verification_email():
#     applicant = self.user
#     template_values = {
#         'verifier': "Amazing Position Test User",
#         'applicant': applicant,
#         'verification_url': "/"
#     }
