from fastapi import FastAPI
from app.api.v1.endpoints import users, blogs
from app.database import engine, Base
import uvicorn

# Create all tables (in production, use Alembic migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Powered Blog Post Creation API",
    description="API for managing users and AI-generated blog posts.",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc UI
    openapi_url="/openapi.json"  # The generated OpenAPI schema
)

# Include routers from endpoints
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(blogs.router, prefix="/api/v1/blogs", tags=["blogs"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
