from app.extensions import db
from app.models import BusinessProfile, Experience, Role, User


def test_homepage_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Inside Bridge" in response.data


def test_public_catalog_loads(client):
    response = client.get("/experiences/")
    assert response.status_code == 200
    assert b"Experiencias locales aprobadas" in response.data


def test_register_business_creates_expected_role(client, app):
    register_response = client.post(
        "/auth/register",
        data={
            "name": "Business User",
            "email": "business@example.com",
            "password": "password123",
            "role": "business",
        },
        follow_redirects=True,
    )

    assert register_response.status_code == 200
    assert b"Mi negocio" in register_response.data

    with app.app_context():
        user = User.query.filter_by(email="business@example.com").first()
        assert user is not None
        assert user.role.name == "business"


def test_register_tourist_redirects_to_catalog(client, app):
    response = client.post(
        "/auth/register",
        data={
            "name": "Tourist User",
            "email": "tourist@example.com",
            "password": "password123",
            "role": "tourist",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Experiencias locales aprobadas" in response.data

    with app.app_context():
        user = User.query.filter_by(email="tourist@example.com").first()
        assert user.role.name == "tourist"


def create_user(email, role_name, name="Test User"):
    role = Role.query.filter_by(name=role_name).first()
    user = User(email=email, name=name, role=role)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user


def login(client, email):
    return client.post(
        "/auth/login",
        data={"email": email, "password": "password123"},
        follow_redirects=True,
    )


def create_business_with_experience(status=Experience.STATUS_PENDING):
    user = create_user("owner@example.com", "business", "Owner")
    business = BusinessProfile(
        user=user,
        business_name="Mercado Local",
        description="Experiencias de barrio para visitantes.",
        city="Ciudad de Mexico",
        address_area="Roma Norte",
        whatsapp="+525512345678",
        contact_email="hola@mercado.test",
    )
    experience = Experience(
        business=business,
        title_es="Tour de tacos",
        title_en="Taco tour",
        description_es="Una ruta de tacos locales.",
        description_en="A local taco route.",
        category="Gastronomia",
        price_amount=500,
        duration="2 horas",
        city="Ciudad de Mexico",
        address_area="Roma Norte",
        languages="es,en",
        contact_whatsapp="+525512345678",
        status=status,
    )
    db.session.add_all([business, experience])
    db.session.commit()
    return user, business, experience

def test_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_business_can_create_profile_and_pending_experience(client, app):
    with app.app_context():
        create_user("business-create@example.com", "business", "Creator")

    login(client, "business-create@example.com")
    profile_response = client.post(
        "/business/profile",
        data={
            "business_name": "Cafe Centro",
            "description": "Cafe local cerca del centro historico.",
            "city": "Ciudad de Mexico",
            "address_area": "Centro Historico",
            "whatsapp": "+525500000000",
            "contact_email": "cafe@example.com",
            "website_url": "",
        },
        follow_redirects=True,
    )
    assert profile_response.status_code == 200
    assert b"Cafe Centro" in profile_response.data

    experience_response = client.post(
        "/business/experiences/new",
        data={
            "title_es": "Cata de cafe",
            "title_en": "Coffee tasting",
            "description_es": "Prueba cafes mexicanos.",
            "description_en": "Taste Mexican coffee.",
            "category": "Gastronomia",
            "price_amount": "250",
            "duration": "1 hora",
            "city": "Ciudad de Mexico",
            "address_area": "Centro Historico",
            "languages": ["es", "en"],
            "contact_whatsapp": "+525500000000",
            "contact_email": "cafe@example.com",
            "image_url": "",
        },
        follow_redirects=True,
    )
    assert experience_response.status_code == 200
    assert b"Pendiente" in experience_response.data

    with app.app_context():
        experience = Experience.query.filter_by(title_es="Cata de cafe").first()
        assert experience.status == Experience.STATUS_PENDING


def test_pending_experience_is_hidden_until_admin_approves(client, app):
    with app.app_context():
        _, _, experience = create_business_with_experience()
        experience_id = experience.id
        admin = create_user("admin@example.com", "admin", "Admin")
        admin_id = admin.id

    catalog_response = client.get("/experiences/")
    assert b"Tour de tacos" not in catalog_response.data

    login(client, "admin@example.com")
    approve_response = client.post(f"/admin/experiences/{experience_id}/approve", follow_redirects=True)
    assert approve_response.status_code == 200
    assert b"Experiencia aprobada" in approve_response.data

    catalog_response = client.get("/experiences/")
    assert b"Tour de tacos" in catalog_response.data

    detail_response = client.get(f"/experiences/{experience_id}")
    assert detail_response.status_code == 200
    assert b"Taco tour" in detail_response.data

    with app.app_context():
        admin = db.session.get(User, admin_id)
        assert admin.is_admin


def test_business_cannot_edit_other_business_experience(client, app):
    with app.app_context():
        _, _, experience = create_business_with_experience()
        create_user("other@example.com", "business", "Other")
        experience_id = experience.id

    login(client, "other@example.com")
    response = client.get(f"/business/experiences/{experience_id}/edit")
    assert response.status_code == 403


def test_non_admin_cannot_moderate(client, app):
    with app.app_context():
        _, _, experience = create_business_with_experience()
        experience_id = experience.id

    login(client, "owner@example.com")
    response = client.post(f"/admin/experiences/{experience_id}/approve")
    assert response.status_code == 403
