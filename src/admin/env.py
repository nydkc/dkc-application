import html
import io
import os
from flask import request, send_file, Blueprint
from common.util import generate_pdf
from admin.auth.login_manager import admin_login_required


env_bp = Blueprint("admin_env", __name__)


@env_bp.route("/env")
@admin_login_required
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
