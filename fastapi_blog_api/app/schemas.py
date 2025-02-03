from pydantic import BaseModel, Field
from typing import Optional

# User schemas
class UserCreate(BaseModel):
    username: str = Field(..., max_length=50)
    password: str = Field(..., min_length=6)

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True
        
        
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
# BlogPost schemas
class BlogPostBase(BaseModel):
    title: str = Field(..., max_length=150)
    content: Optional[str] = None

class BlogPostCreate(BlogPostBase):
    pass

class BlogPostUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=150)
    content: Optional[str] = None


class BlogPostOut(BlogPostBase):
    id: int
    status: str
    owner_id: int

    class Config:
        orm_mode = True
