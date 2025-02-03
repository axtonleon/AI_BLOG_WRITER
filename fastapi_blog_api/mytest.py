import requests
import json
import uuid
import time
import os
from app.core.security import get_password_hash
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/api/v1")  # Use environment variable or default


def create_user(username, password):
    """Creates a user and returns the username and password"""
    print("Creating user...")
    user_data = {"username": username, "password": password}
    print(f"  Request data: {user_data}")
    response = requests.post(f"{BASE_URL}/users/register", json=user_data)
    response.raise_for_status()
    print(f"  User created successfully! username: {username}, status code: {response.status_code}")
    return username, password


def get_access_token(username, password):
    """Retrieves an access token for a user."""
    print("Getting access token...")
    user_data = {"username": username, "password": password}
    print(f"  Request data: {user_data}")
    response = requests.post(f"{BASE_URL}/users/login", json=user_data)
    response.raise_for_status()
    access_token = response.json()["access_token"]
    print(f"  Access token retrieved successfully!, status code: {response.status_code}")
    return access_token


def create_blog_post(access_token, title):
    """Creates a blog post and waits for completion."""
    print("Creating blog post...")
    headers = {"Authorization": f"Bearer {access_token}"}
    print(f"  Headers: {headers}")
    blog_data = {"title": title}
    print(f"  Request data: {blog_data}")
    response = requests.post(f"{BASE_URL}/blogs", headers=headers, json=blog_data)
    response.raise_for_status()
    created_blog = response.json()
    print(f"  Blog created with status code: {response.status_code} and details: {created_blog}")
    blog_id = created_blog["id"]

    while True:
        print(f"Polling blog post {blog_id} for completion...")
        blog_response = get_blog_post_by_id(access_token, blog_id)
        if blog_response.get("status") == "completed":
            print(f"  Blog status is completed!")
            return blog_response
        time.sleep(1)  # You can adjust the poll rate if needed.


def get_blog_posts(access_token):
    """Retrieves all blog posts."""
    print("Getting blog posts...")
    headers = {"Authorization": f"Bearer {access_token}"}
    print(f"  Headers: {headers}")
    response = requests.get(f"{BASE_URL}/blogs", headers=headers)
    response.raise_for_status()
    blogs = response.json()
    print(f"  Blog posts: {blogs}, status code {response.status_code}")
    return blogs


def get_blog_post_by_id(access_token, blog_id):
    """Retrieves a blog post by its ID."""
    print(f"Getting blog post by ID: {blog_id}...")
    headers = {"Authorization": f"Bearer {access_token}"}
    print(f"  Headers: {headers}")
    response = requests.get(f"{BASE_URL}/blogs/{blog_id}", headers=headers)
    response.raise_for_status()
    blog = response.json()
    print(f"  Blog: {blog}, status code {response.status_code}")
    return blog


def update_blog_post(access_token, blog_id, title, content):
    """Updates a blog post."""
    print(f"Updating blog post by ID: {blog_id}...")
    headers = {"Authorization": f"Bearer {access_token}"}
    print(f"  Headers: {headers}")
    update_data = {"title": title, "content": content}
    print(f"  Request data: {update_data}")
    response = requests.put(f"{BASE_URL}/blogs/{blog_id}", headers=headers, json=update_data)
    response.raise_for_status()
    updated_blog = response.json()
    print(f"  Updated blog: {updated_blog}, status code: {response.status_code}")
    return updated_blog


def delete_blog_post(access_token, blog_id):
    """Deletes a blog post."""
    print(f"Deleting blog post by ID: {blog_id}...")
    headers = {"Authorization": f"Bearer {access_token}"}
    print(f"  Headers: {headers}")
    response = requests.delete(f"{BASE_URL}/blogs/{blog_id}", headers=headers)
    print(f"  Response status code: {response.status_code}")
    response.raise_for_status()

def assert_blog_post(blog, title, status):
    """Asserts that a blog has the correct title and status"""
    assert blog["title"] == title, f"Blog title should be {title}, but is {blog.get('title')}"
    assert blog["status"] == status, f"Blog status should be {status} but is {blog.get('status')}"


def test_all_blog_endpoints():
    """Tests all blog endpoints."""
    try:
        # Create a unique username and password
        username = f"testuser_{uuid.uuid4()}"
        password = "testpassword"

        # Create user and get access token
        username, password = create_user(username, password)
        access_token = get_access_token(username, password)

        # Test Create Blog Post
        created_blog = create_blog_post(access_token, title="Initial Blog Post")
        assert_blog_post(created_blog, title="Initial Blog Post", status="completed")


        # Test Get Blog Post By ID
        retrieved_blog = get_blog_post_by_id(access_token, created_blog["id"])
        assert_blog_post(retrieved_blog, title="Initial Blog Post", status="completed")

        # Test Get Blog Posts
        all_blogs = get_blog_posts(access_token)
        assert len(all_blogs) >= 1
        assert any(blog["id"] == created_blog["id"] for blog in all_blogs)

        # Test Update Blog Post
        updated_blog = update_blog_post(
            access_token, created_blog["id"], title="Updated Blog Post", content="This is updated content"
        )
        assert updated_blog["title"] == "Updated Blog Post"
        assert updated_blog["content"] == "This is updated content"

        # Test Get Blog post again with new values
        retrieved_updated_blog = get_blog_post_by_id(access_token, created_blog["id"])
        assert retrieved_updated_blog["title"] == "Updated Blog Post"
        assert retrieved_updated_blog["content"] == "This is updated content"

        
        print("All tests passed!")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        assert False  # Fail test if an exception happens

if __name__ == "__main__":
    test_all_blog_endpoints()