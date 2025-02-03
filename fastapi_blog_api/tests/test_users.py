import pytest
import httpx
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from fastapi_blog_api.main import app 
from app.database import Base, engine
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models import User


@pytest.fixture(scope="module")
def test_app():
  Base.metadata.create_all(bind=engine)
  yield TestClient(app)
  Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
  from app.database import SessionLocal
  db = SessionLocal()
  yield db
  db.close()


def test_register_success(test_app, db_session):
    user_data = {"username": "testuser", "password": "testpassword"}
    response = test_app.post("/api/v1/users/register", json=user_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == user_data["username"]

    # Verify user creation in DB directly
    db_user = db_session.query(User).filter(User.username == user_data["username"]).first()
    assert db_user
    assert db_user.username == user_data["username"]


def test_register_existing_user(test_app, db_session):
    user_data = {"username": "testuser", "password": "testpassword"}
    #First create the user
    test_app.post("/api/v1/users/register", json=user_data)
    
    #Now, register the user again
    response = test_app.post("/api/v1/users/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Username already registered" in response.json()["detail"]

def test_login_success(test_app, db_session):
    user_data = {"username": "testuser", "password": "testpassword"}
    # First register a user
    test_app.post("/api/v1/users/register", json=user_data)

    # Now login using the same credentials
    response = test_app.post("/api/v1/users/login", json=user_data)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials(test_app):
    user_data = {"username": "nonexistent", "password": "wrongpassword"}
    response = test_app.post("/api/v1/users/login", json=user_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid credentials" in response.json()["detail"]