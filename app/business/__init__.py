from flask import Blueprint


business_bp = Blueprint("business", __name__)

from app.business import routes  # noqa: E402,F401
