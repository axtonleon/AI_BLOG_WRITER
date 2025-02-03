from fastapi import FastAPI # Import FastAPI to create the app instance
from app.api.v1.endpoints import users, blogs # Import the user and blog routes
from app.database import engine, Base # Import database engine and base for ORM
import uvicorn # Import uvicorn for running the server

# Create all tables (in production, use Alembic migrations)
Base.metadata.create_all(bind=engine) # Create all database tables defined in SQLAlchemy models

app = FastAPI( # Create the FastAPI app instance
    title="AI-Powered Blog Post Creation API", # API title
    description="API for managing users and AI-generated blog posts.", # API description
    version="1.0.0", # API version
    docs_url="/docs",  # Swagger UI URL
    redoc_url="/redoc",  # ReDoc UI URL
    openapi_url="/openapi.json" # OpenAPI spec URL
)

# Include routers from endpoints
app.include_router(users.router, prefix="/api/v1/users", tags=["users"]) # Include user router with /api/v1/users prefix and tag
app.include_router(blogs.router, prefix="/api/v1/blogs", tags=["blogs"]) # Include blog router with /api/v1/blogs prefix and tag

if __name__ == "__main__":
    """
    Run the FastAPI application using Uvicorn.

    This block starts the Uvicorn server when the script is executed directly.
    It's used for local development.
    """
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) # Run the application using uvicorn
    # "main:app" refers to the FastAPI app instance (app) within the main.py file.
    # host="0.0.0.0" makes the server listen on all network interfaces
    # port=8000 specifies the port for the server
    # reload=True enables hot-reloading for development, changes will be automatically applied when the files are changed