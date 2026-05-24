import os

from flask import Flask

from app.config import config_by_name
from app.extensions import db, login_manager
from app.models import Role


def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)
    config_name = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_by_name.get(config_name, config_by_name["development"]))

    db.init_app(app)
    login_manager.init_app(app)

    from app.admin import admin_bp
    from app.auth import auth_bp
    from app.business import business_bp
    from app.experiences import experiences_bp
    from app.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(experiences_bp, url_prefix="/experiences")
    app.register_blueprint(business_bp, url_prefix="/business")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    register_cli(app)
    return app


def register_cli(app):
    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        Role.seed_defaults()
        db.session.commit()
        print("Database initialized.")

    @app.cli.command("create-admin")
    def create_admin():
        import click

        from app.models import User

        email = click.prompt("Email")
        password = click.prompt("Password", hide_input=True, confirmation_prompt=True)

        db.create_all()
        Role.seed_defaults()
        admin_role = Role.query.filter_by(name="admin").first()

        if User.query.filter_by(email=email.lower()).first():
            raise click.ClickException("A user with that email already exists.")

        user = User(email=email.lower(), name="Admin", role=admin_role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Admin user created: {email}")
