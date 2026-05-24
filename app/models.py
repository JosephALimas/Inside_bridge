from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login_manager


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    users = db.relationship("User", back_populates="role", lazy=True)

    @classmethod
    def seed_defaults(cls):
        defaults = {
            "admin": "Acceso administrativo",
            "business": "Negocio local",
            "tourist": "Visitante o turista",
        }
        for name, description in defaults.items():
            if not cls.query.filter_by(name=name).first():
                db.session.add(cls(name=name, description=description))

    def __repr__(self):
        return f"<Role {self.name}>"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)

    role = db.relationship("Role", back_populates="users")
    business_profile = db.relationship(
        "BusinessProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @property
    def is_admin(self):
        return self.role and self.role.name == "admin"

    @property
    def is_business(self):
        return self.role and self.role.name == "business"

    @property
    def is_tourist(self):
        return self.role and self.role.name == "tourist"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class BusinessProfile(db.Model):
    __tablename__ = "business_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    business_name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(120), nullable=False, default="Ciudad de Mexico")
    address_area = db.Column(db.String(255), nullable=False)
    whatsapp = db.Column(db.String(50), nullable=True)
    contact_email = db.Column(db.String(255), nullable=True)
    website_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = db.relationship("User", back_populates="business_profile")
    experiences = db.relationship(
        "Experience",
        back_populates="business",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def __repr__(self):
        return f"<BusinessProfile {self.business_name}>"


class Experience(db.Model):
    __tablename__ = "experiences"

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUSES = (STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED)

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey("business_profiles.id"), nullable=False)
    title_es = db.Column(db.String(180), nullable=False)
    title_en = db.Column(db.String(180), nullable=False)
    description_es = db.Column(db.Text, nullable=False)
    description_en = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    price_amount = db.Column(db.Float, nullable=True)
    duration = db.Column(db.String(80), nullable=True)
    city = db.Column(db.String(120), nullable=False, default="Ciudad de Mexico")
    address_area = db.Column(db.String(255), nullable=False)
    languages = db.Column(db.String(120), nullable=False, default="es,en")
    contact_whatsapp = db.Column(db.String(50), nullable=True)
    contact_email = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), nullable=False, default=STATUS_PENDING, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    business = db.relationship("BusinessProfile", back_populates="experiences")

    @property
    def display_price(self):
        if self.price_amount is None:
            return "Precio por confirmar"
        return f"${self.price_amount:,.0f} MXN"

    @property
    def language_list(self):
        return [language.strip() for language in self.languages.split(",") if language.strip()]

    def __repr__(self):
        return f"<Experience {self.title_es}>"
