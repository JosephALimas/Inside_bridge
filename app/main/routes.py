from flask import redirect, render_template, url_for
from flask_login import current_user, login_required

from app.main import main_bp


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for("admin.experiences"))
    if current_user.is_business:
        return redirect(url_for("business.dashboard"))
    if current_user.is_tourist:
        return redirect(url_for("experiences.index"))
    return render_template("dashboard.html")
