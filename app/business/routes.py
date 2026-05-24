from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.business import business_bp
from app.decorators import role_required
from app.extensions import db
from app.experiences.routes import CATEGORIES
from app.models import BusinessProfile, Experience


def current_business_profile():
    return BusinessProfile.query.filter_by(user_id=current_user.id).first()


def parse_price(value):
    value = value.strip()
    if not value:
        return None
    return float(value)


def populate_experience(experience, form, business):
    experience.business = business
    experience.title_es = form.get("title_es", "").strip()
    experience.title_en = form.get("title_en", "").strip()
    experience.description_es = form.get("description_es", "").strip()
    experience.description_en = form.get("description_en", "").strip()
    experience.category = form.get("category", "").strip()
    experience.price_amount = parse_price(form.get("price_amount", ""))
    experience.duration = form.get("duration", "").strip()
    experience.city = form.get("city", "Ciudad de Mexico").strip() or "Ciudad de Mexico"
    experience.address_area = form.get("address_area", "").strip()
    experience.languages = ",".join(form.getlist("languages")) or "es,en"
    experience.contact_whatsapp = form.get("contact_whatsapp", "").strip()
    experience.contact_email = form.get("contact_email", "").strip()
    experience.image_url = form.get("image_url", "").strip()
    experience.status = Experience.STATUS_PENDING
    return experience


def validate_experience_form(form):
    required_fields = [
        "title_es",
        "title_en",
        "description_es",
        "description_en",
        "category",
        "address_area",
    ]
    return all(form.get(field, "").strip() for field in required_fields)


@business_bp.route("/dashboard")
@role_required("business")
def dashboard():
    business = current_business_profile()
    experiences = []
    if business:
        experiences = Experience.query.filter_by(business_id=business.id).order_by(Experience.created_at.desc()).all()
    return render_template("business/dashboard.html", business=business, experiences=experiences)


@business_bp.route("/profile", methods=["GET", "POST"])
@role_required("business")
def profile():
    business = current_business_profile()

    if request.method == "POST":
        business = business or BusinessProfile(user=current_user)
        business.business_name = request.form.get("business_name", "").strip()
        business.description = request.form.get("description", "").strip()
        business.city = request.form.get("city", "Ciudad de Mexico").strip() or "Ciudad de Mexico"
        business.address_area = request.form.get("address_area", "").strip()
        business.whatsapp = request.form.get("whatsapp", "").strip()
        business.contact_email = request.form.get("contact_email", "").strip()
        business.website_url = request.form.get("website_url", "").strip()

        if not business.business_name or not business.description or not business.address_area:
            flash("Nombre, descripcion y zona son obligatorios.", "danger")
            return render_template("business/profile.html", business=business), 400

        db.session.add(business)
        db.session.commit()
        flash("Perfil de negocio guardado.", "success")
        return redirect(url_for("business.dashboard"))

    return render_template("business/profile.html", business=business)


@business_bp.route("/experiences/new", methods=["GET", "POST"])
@role_required("business")
def new_experience():
    business = current_business_profile()
    if not business:
        flash("Primero completa tu perfil de negocio.", "warning")
        return redirect(url_for("business.profile"))

    if request.method == "POST":
        experience = Experience()

        try:
            populate_experience(experience, request.form, business)
        except ValueError:
            flash("El precio debe ser un numero valido.", "danger")
            return render_template("business/experience_form.html", experience=experience, categories=CATEGORIES), 400

        if not validate_experience_form(request.form):
            flash("Completa los campos obligatorios de la experiencia.", "danger")
            return render_template("business/experience_form.html", experience=experience, categories=CATEGORIES), 400

        db.session.add(experience)
        db.session.commit()
        flash("Experiencia enviada a revision.", "success")
        return redirect(url_for("business.dashboard"))

    return render_template("business/experience_form.html", experience=None, categories=CATEGORIES)


@business_bp.route("/experiences/<int:experience_id>/edit", methods=["GET", "POST"])
@role_required("business")
def edit_experience(experience_id):
    business = current_business_profile()
    experience = db.get_or_404(Experience, experience_id)
    if not business or experience.business_id != business.id:
        abort(403)

    if request.method == "POST":
        try:
            populate_experience(experience, request.form, business)
        except ValueError:
            flash("El precio debe ser un numero valido.", "danger")
            return render_template("business/experience_form.html", experience=experience, categories=CATEGORIES), 400

        if not validate_experience_form(request.form):
            flash("Completa los campos obligatorios de la experiencia.", "danger")
            return render_template("business/experience_form.html", experience=experience, categories=CATEGORIES), 400

        db.session.commit()
        flash("Experiencia actualizada y enviada a revision.", "success")
        return redirect(url_for("business.dashboard"))

    return render_template("business/experience_form.html", experience=experience, categories=CATEGORIES)
