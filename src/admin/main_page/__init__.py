from flask import Blueprint

main_page_bp = Blueprint("admin.main_page", __name__, template_folder="templates")
