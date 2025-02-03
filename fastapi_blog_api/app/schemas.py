from pydantic import BaseModel, Field
from typing import Optional

# User schemas
class UserCreate(BaseModel):
    """
    Pydantic model for creating a new user.

    Attributes:
        username (str): The username of the user, max length 50, required.
        password (str): The password of the user, min length 6, required.
    """
    username: str = Field(..., max_length=50, description="Username of the user")
    password: str = Field(..., min_length=6, description="Password of the user")

class UserOut(BaseModel):
    """
    Pydantic model for outputting user information.

    Attributes:
        id (int): The unique ID of the user.
        username (str): The username of the user.
    """
    id: int = Field(description="Unique ID of the user")
    username: str = Field(description="Username of the user")

    class Config:
        """Configuration for Pydantic model."""
        orm_mode = True # Enables ORM mode for compatibility with SQLAlchemy models
        
class Token(BaseModel):
    """
    Pydantic model for authentication token.
    
    Attributes:
        access_token (str): The access token string
        token_type (str): The type of token
    """
    access_token: str = Field(description="Access token string")
    token_type: str = Field(description="Type of the token")

class TokenData(BaseModel):
    """
    Pydantic model for token data.

    Attributes:
         username (Optional[str]): Username of the user in token
    """
    username: Optional[str] = Field(default=None, description="Username in the token")

# BlogPost schemas
class BlogPostBase(BaseModel):
    """
    Base Pydantic model for blog post data.

    Attributes:
        title (str): The title of the blog post, max length 150, required.
        content (Optional[str]): The content of the blog post (optional).
    """
    title: str = Field(..., max_length=150, description="Title of the blog post")
    content: Optional[str] = Field(default=None, description="Content of the blog post")

class BlogPostCreate(BlogPostBase):
    """
    Pydantic model for creating a new blog post, inherits from BlogPostBase
    """
    pass

class BlogPostUpdate(BaseModel):
    """
    Pydantic model for updating an existing blog post.

    Attributes:
        title (Optional[str]): The title of the blog post, max length 150, optional.
        content (Optional[str]): The content of the blog post (optional).
    """
    title: Optional[str] = Field(default=None, max_length=150, description="Title of the blog post")
    content: Optional[str] = Field(default=None, description="Content of the blog post")


class BlogPostOut(BlogPostBase):
    """
    Pydantic model for outputting blog post data.

    Attributes:
        id (int): The unique ID of the blog post.
        status (str): The status of the blog post.
        owner_id (int): The ID of the user who owns the blog post.
    """
    id: int = Field(description="Unique ID of the blog post")
    status: str = Field(description="Status of the blog post")
    owner_id: int = Field(description="ID of the user who owns the blog post")

    class Config:
        """Configuration for Pydantic model."""
        orm_mode = True # Enables ORM mode for compatibility with SQLAlchemy models