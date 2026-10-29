from sqlalchemy import select

from job_aggregator.db.models.user import User

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/token"
PASSWORD = "Strong-password-123!"


def register(client, email, password=PASSWORD):
    return client.post(REGISTER_URL, json={"email": email, "password": password})


def login(client, email, password=PASSWORD):
    return client.post(LOGIN_URL, json={"email": email, "password": password})


def test_register_user(client):
    response = register(client, "new-user@example.com")

    assert response.status_code == 201
    assert response.json()["email"] == "new-user@example.com"
    assert not {"password", "hashed_password"} & response.json().keys()


def test_register_normalizes_email(client, db_session):
    response = register(client, " Foo@Example.com ")

    assert response.status_code == 201
    assert response.json()["email"] == "foo@example.com"
    user = db_session.scalar(select(User).where(User.email == "foo@example.com"))
    assert user is not None


def test_register_validation(client):
    assert register(client, "not-an-email").status_code == 422
    assert register(client, "short-password@example.com", "short").status_code == 422


def test_register_duplicate_email(client):
    assert register(client, "duplicate@example.com").status_code == 201
    response = register(client, "DUPLICATE@example.com")

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"


def test_login_success(client):
    assert register(client, "login@example.com").status_code == 201

    response = login(client, "LOGIN@example.com")

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_rejects_invalid_credentials(client, db_session):
    assert login(client, "unknown@example.com").status_code == 401
    assert register(client, "wrong-password@example.com").status_code == 201

    response = login(client, "wrong-password@example.com", "Wrong-password-456!")
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
    assert response.headers["www-authenticate"] == "Bearer"
