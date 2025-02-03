
# AI-Powered Blog Post Creation API

This repository implements an AI-powered blog post creation API using FastAPI and a multi-agent architecture provided by the `smoltools` package. The application supports user registration, authentication, and dynamic blog post creation powered by an AI agent system that handles research, content generation, and editing in the background.

## Features

*   **User Management:** Secure registration and authentication using JWT.
*   **Blog Post Management:** Create, retrieve, update, and delete blog posts linked to authenticated users.
*   **AI-Powered Content Generation:** Leverages a multi-agent system for researching, drafting, and editing blog posts.
*   **Asynchronous Background Processing:** Long-running AI tasks are managed asynchronously to ensure a responsive API.
*   **Database Integration:** Uses SQLite with SQLAlchemy ORM and Alembic for database migrations.
*   **Interactive API Documentation:** Automatically generated Swagger UI available via FastAPI.
*   **Configurable:** Allows configuration through environment variables.

## Tech Stack

*   **FastAPI:** A modern, fast (high-performance) web framework for building APIs with Python.
*   **SQLite & SQLAlchemy:** Lightweight database engine and ORM for data modeling.
*   **Alembic:** Database migrations tool.
*   **JWT:** JSON Web Tokens for stateless authentication.
*   **`smoltools`:** Multi-agent toolkit for orchestrating AI-powered tasks.
*   **Pydantic:** Data validation and settings management.
*   **Uvicorn:** ASGI server for running the FastAPI application.
*   **pytest:** Testing framework for Python.
*   **python-dotenv:** For loading environment variables from a `.env` file.

## Getting Started

### Prerequisites

*   Python 3.8 or higher
*   Git

### Clone the Repository

```bash
git clone https://github.com/axtonleon/AI_BLOG_WRITER.git
cd AI_BLOG_WRITER
```

### Create and Activate a Virtual Environment

```bash
python -m venv venv
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

1.  Copy the provided example file:

    ```bash
    cp .env.example .env
    ```

2.  Update the variables in `.env` as needed. The following environment variables are used by the application:

    *   `SECRET_KEY`: The secret key used to sign JWT tokens (must be set).
    *   `ALGORITHM`: The JWT algorithm (default is `HS256`).
    *   `ACCESS_TOKEN_EXPIRE_MINUTES`: The token expiry time in minutes (default is 15).
    *   `DATABASE_URL`: The database URL for SQLAlchemy.
    *   `TEST_DATABASE_FILE`: The name of the database file for testing.
    *   `JINA_API_KEY`: The API key for using Jina AI features. (You will need to obtain this key separately from the Jina AI website).
    *   `OPENAI_API_KEY`: The API key for using OpenAI features needed by the `smoltools` library.
    *   `BASE_URL`: The base URL for API endpoints (default is `http://localhost:8000/api/v1`).

    **Note:** The `.env` file should be in the same directory as  `main.py` file, or in the directory that you run your server from. It is recommended that you put your `.env` file in the same directory as the `fastapi_blog_api` folder.

### Run the application

Start the development server using Uvicorn:

```bash
cd fastapi_blog_api
uvicorn main:app --reload
```

The API is now available at: `http://127.0.0.1:8000`

Access the interactive API docs at: `http://localhost:8000/docs`

## API Endpoints

All API endpoints are versioned under `/api/v1/`.

### User Endpoints

#### `POST /api/v1/users/register`

*   **Description:**
    Registers a new user. This endpoint accepts a JSON payload containing a `username` and `password`, hashes the password, and stores the user in the SQLite database.
*   **Request Body Example:**

    ```json
    {
      "username": "exampleuser",
      "password": "examplepass123"
    }
    ```

*   **Response Example:**

    ```json
    {
      "id": 1,
      "username": "exampleuser"
    }
    ```

#### `POST /api/v1/users/login`

*   **Description:**
    Authenticates an existing user. Upon providing a valid username and password, this endpoint returns a JWT access token that is used to authenticate subsequent requests.
*   **Request Body Example:**

    ```json
    {
      "username": "exampleuser",
      "password": "examplepass123"
    }
    ```

*   **Response Example:**

    ```json
    {
      "access_token": "your_jwt_token_here",
      "token_type": "bearer"
    }
    ```

### Blog Post Endpoints

#### `POST /api/v1/blogs`

*   **Description:**
    Creates a new blog post entry. This endpoint accepts a JSON payload with a blog post `title`. Once the blog post entry is created, a background task is triggered to generate the blog post content using the AI-powered multi-agent system.
*   **Request Body Example:**

    ```json
    {
      "title": "Top 5 Products Released at CES 2025"
    }
    ```

*   **Response Example:**

    ```json
    {
      "id": 1,
      "title": "Top 5 Products Released at CES 2025",
      "content": "",
      "status": "pending",
      "owner_id": 1
    }
    ```

#### `GET /api/v1/blogs`

*   **Description:**
    Retrieves a list of all blog posts associated with the authenticated user.
*   **Response Example:**

    ```json
    [
      {
        "id": 1,
        "title": "Top 5 Products Released at CES 2025",
        "content": "Generated content will appear here once processing is complete.",
        "status": "completed",
        "owner_id": 1
      }
    ]
    ```

#### `GET /api/v1/blogs/{blog_id}`

*   **Description:**
    Retrieves a single blog post by its ID for the authenticated user. This endpoint is useful for checking the status or content of a specific blog post.
*   **Response Example:**

    ```json
    {
      "id": 1,
      "title": "Top 5 Products Released at CES 2025",
      "content": "Generated content will appear here once processing is complete.",
      "status": "completed",
      "owner_id": 1
    }
    ```

#### `PUT /api/v1/blogs/{blog_id}`

*   **Description:**
    Updates an existing blog post. The endpoint accepts a JSON payload with fields that can be updated (`title` and/or `content`). This allows users to modify the blog post if needed.
*   **Request Body Example:**

    ```json
    {
      "title": "Updated Blog Post Title",
      "content": "Updated content..."
    }
    ```

*   **Response Example:**

    ```json
    {
      "id": 1,
      "title": "Updated Blog Post Title",
      "content": "Updated content...",
      "status": "completed",
      "owner_id": 1
    }
    ```

#### `DELETE /api/v1/blogs/{blog_id}`

*   **Description:**
    Deletes a specific blog post belonging to the authenticated user. This endpoint does not return a body on successful deletion.
*   **Response:**
    HTTP 204 No Content

## Testing

This project uses `pytest` for testing. To run the tests, execute:

```bash
cd fastapi_blog_api
pytest
```

Ensure all tests pass before deploying or making significant changes.

## Design Decisions and Rationale

*   **Modular Architecture:** The application is designed with a clear separation of concerns, dividing code into models, schemas, API endpoints, and background processing logic. This enhances maintainability and scalability.
*   **Asynchronous Background Tasks:**  Long-running AI operations are handled outside the main request-response cycle using FastAPI's `BackgroundTasks`, which improves API responsiveness and performance.
*   **Multi-Agent AI Integration:** The API uses multiple AI agents that are part of the `smoltools` library, which creates an efficient pipeline for blog post creation, with research, writing, and editing agents.
*   **Security First:** The API implements JSON Web Tokens (JWT) for secure user authentication. It uses best practices for password hashing with `passlib` to prevent password leakage.
*   **Configurable Environment:** The application's behavior is easily adjusted with environment variables, such as API keys and database locations.
*   **Testable Code**: Code has been created to be testable by using dependency injection and other best practices.

## Assumptions Made

*   **SQLite for Development:** SQLite is used as the primary database for simplicity, especially for local development. However, this is not recommended for production, and the `DATABASE_URL` variable can be set to connect to other SQL databases such as PostgresSQL.
*   **API Key Management:** It is assumed that users will configure environment variables correctly and securely manage their API keys, including the `JINA_API_KEY` and the `OPENAI_API_KEY`.
*   **AI Agent Capabilities:** This API assumes the AI agent is able to generate content, but does not do any error checking on the quality of the content.
*   **Email**: The application assumes that the users will be authenticating via username/password, it does not send out any emails to create user accounts.
*   **No Rate Limiting:** There is no rate limiting in the API, which is a potential security risk but can be added later.
*   **No Advanced Content Customization:** The application assumes the AI agent will provide the correct content but does not expose a way to customize the AI generation via parameters.

## Future Improvements

*   **Enhanced Error Handling and Logging:** Integrate more robust logging and error management for troubleshooting and monitoring.
*   **Extended AI Capabilities:** Fine-tune and expand AI agents for improved content quality, customizability, and variety.
*   **Dockerization:** Containerize the application for easier deployment and scalability.
*   **CI/CD Integration:** Set up continuous integration and deployment pipelines for automated testing and deployment.
*   **Rate Limiting and Additional Security Measures:** Implement rate limiting and other security measures, such as input sanitization, to protect the API from abuse.
*  **Email verification**: Users must be created via the register endpoint and there is no email verification to ensure they own the provided email.
*   **Database choice:** The project uses `sqlite` as a primary database, but can be configured with an SQL database of your choice.

## Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and write tests as needed.
4.  Submit a pull request with a clear description of your changes.

