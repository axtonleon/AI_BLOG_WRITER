from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Header
from sqlalchemy.orm import Session
from typing import List
from jose import JWTError
from fastapi.security import OAuth2PasswordBearer
from app.models import BlogPost, User
from app.schemas import BlogPostCreate, BlogPostOut, BlogPostUpdate
from app.database import SessionLocal
from app.core import ai_agent, security
from app.core.config import settings

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/users/login")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get the current user from token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = security.decode_access_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        username = payload.get("sub")  # Assuming the token payload has a 'sub' field with username
        if not username:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


@router.post(
    "",
    response_model=BlogPostOut,
    summary="Create a new blog post",
    description="Creates a blog post entry with a title. A background task then generates the blog content using the AI-powered multi-agent system."
)
async def create_blog_post(
    blog: BlogPostCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Create a new blog post entry with a pending status.
    new_blog = BlogPost(title=blog.title, content="", status="pending", owner_id=current_user.id)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    
    # Schedule background task for AI content generation using the new blog writer logic.
    background_tasks.add_task(generate_and_update_blog, new_blog.id, blog.title)
    
    return new_blog
from app.database import SessionLocal
from app.models import BlogPost
from app.core import ai_agent

def generate_and_update_blog(blog_id: int, topic: str):
    """
    Background task that calls the multi-agent AI blog writer to generate content and updates the blog post.
    """
    # Create a new session for the background task.
    db = SessionLocal()
    try:
        blog = db.query(BlogPost).filter(BlogPost.id == blog_id).first()
        if not blog:
            return  # Blog post not found

        try:
            # Call the new blog writer logic; adjust the filename if needed.
            content = ai_agent.write_blog_post(topic, output_file=f"blog_post_{blog_id}.md")
            if isinstance(content, dict):
                if "answer" in content:
                    blog.content = content["answer"]
                else:
                    blog.content = str(content) # Fallback if there is no "answer"
            elif isinstance(content, str):
                 blog.content = content
            else:
                blog.content = str(content) #Another fallback just in case content is something else

            blog.status = "completed"
        except Exception as e:
            blog.content = f"Error generating content: {str(e)}"
            blog.status = "failed"

        db.commit()
    finally:
        db.close()
@router.get(
    "",
    response_model=List[BlogPostOut],
    summary="Retrieve all blog posts",
    description="Fetches all blog posts associated with the authenticated user."
)
async def get_blog_posts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    blogs = db.query(BlogPost).filter(BlogPost.owner_id == current_user.id).all()
    return blogs

@router.get(
    "/{blog_id}",
    response_model=BlogPostOut,
    summary="Retrieve a single blog post",
    description="Fetches a specific blog post by its ID for the authenticated user."
)
async def get_blog_post(blog_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    blog = db.query(BlogPost).filter(BlogPost.id == blog_id, BlogPost.owner_id == current_user.id).first()
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Blog post not found"
        )
    return blog

@router.put(
    "/{blog_id}",
    response_model=BlogPostOut,
    summary="Update a blog post",
    description="Updates the title and/or content of a blog post for the authenticated user."
)
async def update_blog_post(blog_id: int, blog_update: BlogPostUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    blog = db.query(BlogPost).filter(BlogPost.id == blog_id, BlogPost.owner_id == current_user.id).first()
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Blog post not found"
        )
    
    if blog_update.title is not None:
        blog.title = blog_update.title
    if blog_update.content is not None:
        blog.content = blog_update.content
    
    db.commit()
    db.refresh(blog)
    return blog

@router.delete(
    "/{blog_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a blog post",
    description="Deletes a blog post by its ID for the authenticated user."
)
async def delete_blog_post(blog_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    blog = db.query(BlogPost).filter(BlogPost.id == blog_id, BlogPost.owner_id == current_user.id).first()
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Blog post not found"
        )
    db.delete(blog)
    db.commit()
    return