from app.models import User


def test_homepage_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Inside Bridge" in response.data


def test_register_login_and_dashboard(client, app):
    register_response = client.post(
        "/auth/register",
        data={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
        },
        follow_redirects=True,
    )

    assert register_response.status_code == 200
    assert b"Dashboard" in register_response.data

    with app.app_context():
        user = User.query.filter_by(email="test@example.com").first()
        assert user is not None
        assert user.role.name == "member"

    client.post("/auth/logout", follow_redirects=True)
    login_response = client.post(
        "/auth/login",
        data={"email": "test@example.com", "password": "password123"},
        follow_redirects=True,
    )

    assert login_response.status_code == 200
    assert b"Sesion iniciada" in login_response.data


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
