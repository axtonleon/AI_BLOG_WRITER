from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    """
    SQLAlchemy model representing a user in the database.

    Attributes:
        __tablename__ (str): The name of the database table.
        id (Column): The primary key and unique ID of the user.
        username (Column): The username of the user (unique).
        hashed_password (Column): The hashed password of the user.
        blog_posts (relationship): Relationship with BlogPost model.
    """
    __tablename__ = "users" # Specifies the table name in the database
    id = Column(Integer, primary_key=True, index=True, description="Primary key user id") # Primary key column for the User table
    username = Column(String(50), unique=True, index=True, nullable=False, description="Unique username of the user") # Column for storing username
    hashed_password = Column(String, nullable=False, description="User password hashed") # Column for storing hashed password
    blog_posts = relationship("BlogPost", back_populates="owner", cascade="all, delete-orphan", description="Relationship with Blog posts") # Defines relationship to blog posts

class BlogPost(Base):
    """
    SQLAlchemy model representing a blog post in the database.

    Attributes:
        __tablename__ (str): The name of the database table.
        id (Column): The primary key and unique ID of the blog post.
        title (Column): The title of the blog post.
        content (Column): The content of the blog post.
        status (Column): The status of the blog post.
        owner_id (Column): Foreign key referencing the ID of the user who owns the blog post.
        owner (relationship): Relationship with User model.
    """
    __tablename__ = "blog_posts" # Specifies the table name in the database
    id = Column(Integer, primary_key=True, index=True, description="Primary key blog post id") # Primary key column for the blog post
    title = Column(String(150), nullable=False, description="Title of the blog post") # Column for blog post title
    content = Column(Text, nullable=True, description="Content of the blog post") # Column for blog post content
    status = Column(String(50), default="pending", description="Status of the blog post") # Column for status of the blog post, default pending
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, description="Foreign key referencing the User that owns this blog") # Foreign key referencing the owner
    owner = relationship("User", back_populates="blog_posts", description="Relationship with User model") # Defines the relationship with user