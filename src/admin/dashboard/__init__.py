from flask import Blueprint

dashboard_bp = Blueprint('admin.dashboard', __name__, template_folder='templates')
