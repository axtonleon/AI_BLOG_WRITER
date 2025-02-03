import pytest
import httpx
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from fastapi_blog_api.main import app   # Assuming your app is created in main.py
from app.database import Base, engine
from sqlalchemy.orm import Session
from app.models import User, BlogPost
from app.core.security import get_password_hash
from unittest.mock import patch
import time
import uuid # Import the uuid module

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


def create_user_for_tests(db_session, username=None, password="testpassword"):
    if username is None:
         username = f"testuser_{uuid.uuid4()}" # Create a unique username if one is not provided
    hashed_password = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    return new_user

def get_access_token(test_app, username, password="testpassword"): #Now it needs a username argument
    user_data = {"username": username, "password": password}
    login_response = test_app.post("/api/v1/users/login", json=user_data)
    return login_response.json()["access_token"]

@patch("app.api.v1.endpoints.blogs.ai_agent.write_blog_post")
def test_create_blog_post_success(mock_write_blog_post, test_app, db_session):
    mock_write_blog_post.return_value = "This is the blog content from the mock."
    user = create_user_for_tests(db_session) # A unique user will be created with uuid
    access_token = get_access_token(test_app, username = user.username)  # Pass in username
    blog_data = {"title": "Test Blog Title"}
    response = test_app.post(
        "/api/v1/blogs",
        json=blog_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == blog_data["title"]
    assert response.json()["status"] == "pending"

    time.sleep(0.1) # small pause to make sure that the background task was finished
    db_blog = db_session.query(BlogPost).filter(BlogPost.id == response.json()["id"]).first()
    assert db_blog.status == "completed"
    assert db_blog.content == "This is the blog content from the mock."


def test_create_blog_post_unauthorized(test_app):
    blog_data = {"title": "Test Blog Title"}
    response = test_app.post(
        "/api/v1/blogs",
        json=blog_data,
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid token" in response.json()["detail"]

@patch("app.api.v1.endpoints.blogs.ai_agent.write_blog_post")
def test_get_blog_posts_success(mock_write_blog_post, test_app, db_session):
    mock_write_blog_post.return_value = "This is the blog content from the mock."
    user = create_user_for_tests(db_session) # New unique user will be created with uuid
    access_token = get_access_token(test_app, username = user.username) # Pass in username

    # create two blog posts for this user
    test_app.post(
        "/api/v1/blogs",
        json={"title": "Test Blog 1"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    test_app.post(
        "/api/v1/blogs",
        json={"title": "Test Blog 2"},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    response = test_app.get(
        "/api/v1/blogs",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    assert response.json()[0]["owner_id"] == user.id

def test_get_blog_posts_unauthorized(test_app):
    response = test_app.get(
        "/api/v1/blogs",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid token" in response.json()["detail"]


@patch("app.api.v1.endpoints.blogs.ai_agent.write_blog_post")
def test_get_blog_post_by_id_success(mock_write_blog_post, test_app, db_session):
    mock_write_blog_post.return_value = "This is the blog content from the mock."
    user = create_user_for_tests(db_session) # Create a new unique user
    access_token = get_access_token(test_app, username=user.username) # Pass in username

    blog_data = {"title": "Test Blog"}
    blog_creation_response = test_app.post(
        "/api/v1/blogs",
        json=blog_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    blog_id = blog_creation_response.json()["id"]

    response = test_app.get(
        f"/api/v1/blogs/{blog_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == blog_data["title"]
    assert response.json()["owner_id"] == user.id


def test_get_blog_post_by_id_not_found(test_app, db_session):
    user = create_user_for_tests(db_session) #Create a new unique user
    access_token = get_access_token(test_app, username = user.username) # Pass in username
    response = test_app.get(
        "/api/v1/blogs/999",  # Non-existent ID
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Blog post not found" in response.json()["detail"]

def test_get_blog_post_by_id_unauthorized(test_app):
   response = test_app.get(
        "/api/v1/blogs/1",
        headers={"Authorization": "Bearer invalid_token"}
    )
   assert response.status_code == status.HTTP_401_UNAUTHORIZED
   assert "Invalid token" in response.json()["detail"]

@patch("app.api.v1.endpoints.blogs.ai_agent.write_blog_post")
def test_update_blog_post_success(mock_write_blog_post, test_app, db_session):
    mock_write_blog_post.return_value = "This is the blog content from the mock."
    user = create_user_for_tests(db_session) # Create new unique user
    access_token = get_access_token(test_app, username = user.username) #Pass in username

    # Create a blog post first
    blog_creation_response = test_app.post(
      "/api/v1/blogs",
      json={"title": "Original Blog Title"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    blog_id = blog_creation_response.json()["id"]

    updated_data = {"title": "Updated Blog Title", "content": "Updated blog content"}
    response = test_app.put(
        f"/api/v1/blogs/{blog_id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == updated_data["title"]
    assert response.json()["content"] == updated_data["content"]

def test_update_blog_post_not_found(test_app, db_session):
   user = create_user_for_tests(db_session)  #Create new unique user
   access_token = get_access_token(test_app, username = user.username) #Pass in username

   updated_data = {"title": "Updated Blog Title", "content": "Updated blog content"}
   response = test_app.put(
      f"/api/v1/blogs/999",
      json=updated_data,
      headers={"Authorization": f"Bearer {access_token}"}
   )
   assert response.status_code == status.HTTP_404_NOT_FOUND
   assert "Blog post not found" in response.json()["detail"]

def test_update_blog_post_unauthorized(test_app):
    updated_data = {"title": "Updated Blog Title", "content": "Updated blog content"}
    response = test_app.put(
        "/api/v1/blogs/1",
        json=updated_data,
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid token" in response.json()["detail"]


@patch("app.api.v1.endpoints.blogs.ai_agent.write_blog_post")
def test_delete_blog_post_success(mock_write_blog_post, test_app, db_session):
    mock_write_blog_post.return_value = "This is the blog content from the mock."
    user = create_user_for_tests(db_session) #Create a new unique user
    access_token = get_access_token(test_app, username = user.username) #Pass in username

    blog_creation_response = test_app.post(
      "/api/v1/blogs",
      json={"title": "Blog to be deleted"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    blog_id = blog_creation_response.json()["id"]

    response = test_app.delete(
        f"/api/v1/blogs/{blog_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's actually gone from DB
    db_blog = db_session.query(BlogPost).filter(BlogPost.id == blog_id).first()
    assert db_blog is None


def test_delete_blog_post_not_found(test_app, db_session):
   user = create_user_for_tests(db_session) #Create a new unique user
   access_token = get_access_token(test_app, username = user.username) #Pass in username

   response = test_app.delete(
      f"/api/v1/blogs/999",
        headers={"Authorization": f"Bearer {access_token}"}
   )
   assert response.status_code == status.HTTP_404_NOT_FOUND
   assert "Blog post not found" in response.json()["detail"]

def test_delete_blog_post_unauthorized(test_app):
    response = test_app.delete(
        "/api/v1/blogs/1",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid token" in response.json()["detail"]