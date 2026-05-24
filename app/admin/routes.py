from flask import flash, redirect, render_template, url_for

from app.admin import admin_bp
from app.decorators import role_required
from app.extensions import db
from app.models import Experience


@admin_bp.route("/experiences")
@role_required("admin")
def experiences():
    pending = Experience.query.filter_by(status=Experience.STATUS_PENDING).order_by(Experience.created_at.asc()).all()
    reviewed = (
        Experience.query.filter(Experience.status != Experience.STATUS_PENDING)
        .order_by(Experience.updated_at.desc())
        .all()
    )
    return render_template("admin/experiences.html", pending=pending, reviewed=reviewed)


@admin_bp.route("/experiences/<int:experience_id>/approve", methods=["POST"])
@role_required("admin")
def approve_experience(experience_id):
    experience = db.get_or_404(Experience, experience_id)
    experience.status = Experience.STATUS_APPROVED
    db.session.commit()
    flash("Experiencia aprobada.", "success")
    return redirect(url_for("admin.experiences"))


@admin_bp.route("/experiences/<int:experience_id>/reject", methods=["POST"])
@role_required("admin")
def reject_experience(experience_id):
    experience = db.get_or_404(Experience, experience_id)
    experience.status = Experience.STATUS_REJECTED
    db.session.commit()
    flash("Experiencia rechazada.", "info")
    return redirect(url_for("admin.experiences"))
