from flask import abort, render_template, request

from app.experiences import experiences_bp
from app.extensions import db
from app.models import Experience


CATEGORIES = [
    "Gastronomia",
    "Cultura",
    "Vida nocturna",
    "Compras locales",
    "Deportes",
    "Tours",
]


@experiences_bp.route("/")
def index():
    category = request.args.get("category", "").strip()
    language = request.args.get("language", "").strip().lower()
    price_max = request.args.get("price_max", "").strip()

    query = Experience.query.filter_by(status=Experience.STATUS_APPROVED)

    if category:
        query = query.filter(Experience.category == category)

    if language in {"es", "en"}:
        query = query.filter(Experience.languages.like(f"%{language}%"))

    if price_max:
        try:
            query = query.filter(Experience.price_amount <= float(price_max))
        except ValueError:
            price_max = ""

    experiences = query.order_by(Experience.created_at.desc()).all()
    return render_template(
        "experiences/index.html",
        experiences=experiences,
        categories=CATEGORIES,
        selected_category=category,
        selected_language=language,
        price_max=price_max,
    )


@experiences_bp.route("/<int:experience_id>")
def detail(experience_id):
    experience = db.get_or_404(Experience, experience_id)
    if experience.status != Experience.STATUS_APPROVED:
        abort(404)
    return render_template("experiences/detail.html", experience=experience)
