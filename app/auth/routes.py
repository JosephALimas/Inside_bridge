from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from app.auth import auth_bp
from app.extensions import db
from app.models import Role, User


def redirect_for_user(user):
    if user.is_admin:
        return redirect(url_for("admin.experiences"))
    if user.is_business:
        return redirect(url_for("business.dashboard"))
    return redirect(url_for("experiences.index"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect_for_user(current_user)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role_name = request.form.get("role", "tourist")

        if role_name not in {"tourist", "business"}:
            role_name = "tourist"

        if not name or not email or not password:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template("auth/register.html"), 400

        if User.query.filter_by(email=email).first():
            flash("Ya existe una cuenta con ese correo.", "warning")
            return render_template("auth/register.html"), 409

        Role.seed_defaults()
        role = Role.query.filter_by(name=role_name).first()
        user = User(name=name, email=email, role=role)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Cuenta creada correctamente.", "success")
        return redirect_for_user(user)

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect_for_user(current_user)

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Correo o contrasena incorrectos.", "danger")
            return render_template("auth/login.html"), 401

        login_user(user, remember=remember)
        flash("Bienvenido de vuelta.", "success")
        next_url = request.args.get("next")
        return redirect(next_url or redirect_for_user(user).location)

    return render_template("auth/login.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    flash("Sesion cerrada.", "info")
    return redirect(url_for("main.index"))
