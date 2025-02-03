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
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, comment="Primary key user id")  # Changed to comment
    username = Column(String(50), unique=True, index=True, nullable=False, comment="Unique username of the user")  # Changed to comment
    hashed_password = Column(String, nullable=False, comment="User password hashed")  # Changed to comment
    blog_posts = relationship("BlogPost", back_populates="owner", cascade="all, delete-orphan")  # Removed description

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
    __tablename__ = "blog_posts"
    id = Column(Integer, primary_key=True, index=True, comment="Primary key blog post id")  # Changed to comment
    title = Column(String(150), nullable=False, comment="Title of the blog post")  # Changed to comment
    content = Column(Text, nullable=True, comment="Content of the blog post")  # Changed to comment
    status = Column(String(50), default="pending", comment="Status of the blog post")  # Changed to comment
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="Foreign key referencing the User that owns this blog")  # Changed to comment
    owner = relationship("User", back_populates="blog_posts")  # Removed description