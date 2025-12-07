from flask import Blueprint

application_verification_bp = Blueprint(
    "application_verification", __name__, template_folder="templates"
)
