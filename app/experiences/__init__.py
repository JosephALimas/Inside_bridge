from flask import Blueprint


experiences_bp = Blueprint("experiences", __name__)

from app.experiences import routes  # noqa: E402,F401
