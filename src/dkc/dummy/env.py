import html
import io
import os
from flask import abort, request, render_template, send_file
from common.util import generate_pdf
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
        return send_file(
            io.BytesIO(generate_pdf(response_html)), attachment_filename="env.pdf"
        )
    else:
        return response_html

@dummy_bp.route("/error")
def error():
    return abort(400, description="dummy error")
