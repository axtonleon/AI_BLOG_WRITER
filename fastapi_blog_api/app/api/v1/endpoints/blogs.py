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
    """
    Dependency to get a database session.

    Yields:
        Session: SQLAlchemy database session.
    """
    db = SessionLocal() # Create a new DB session
    try:
        yield db # Yield the session to the request
    finally:
        db.close() # Close the session in the finally block

# Dependency to get the current user from token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Dependency to get the current user from JWT access token.

    Args:
        token (str): The JWT token from authorization header
        db (Session, optional): SQLAlchemy database session.

    Returns:
        User: Current authenticated user.

    Raises:
        HTTPException: If the token is invalid or user is not found.
    """
    try:
        payload = security.decode_access_token(token) # Decodes the token using security utils
        if not payload:
            raise HTTPException( # Raise exception if the token is invalid
                status_code=status.HTTP_401_UNAUTHORIZED, # Set the status code
                detail="Invalid token" # Provide detailed error message
            )
        username = payload.get("sub")  # Assuming the token payload has a 'sub' field with username
        if not username:
             raise HTTPException( # Raise exception if username is not provided
                status_code=status.HTTP_401_UNAUTHORIZED, # Set the status code
                detail="Invalid token" # Provide detailed error message
            )
        user = db.query(User).filter(User.username == username).first() # query the user with username
        if not user:
            raise HTTPException( # Raise exception if user is not found
                status_code=status.HTTP_401_UNAUTHORIZED, # Set the status code
                detail="User not found" # Provide detailed error message
            )
        return user # Return the user
    except JWTError: # Catch JWT Errors during decoding
        raise HTTPException( # Raise exception if token is invalid
            status_code=status.HTTP_401_UNAUTHORIZED, # Set the status code
            detail="Invalid token" # Provide detailed error message
        )


@router.post(
    "", # POST route at root path for creating a blog post
    response_model=BlogPostOut, # Set the expected response model for the endpoint
    summary="Create a new blog post", # Provide a summary description
    description="Creates a blog post entry with a title. A background task then generates the blog content using the AI-powered multi-agent system." # Provide a detailed description
)
async def create_blog_post(
    blog: BlogPostCreate, # Request body data for creating blog post
    background_tasks: BackgroundTasks, # BackgroundTasks object for background task scheduling
    db: Session = Depends(get_db), # Injected DB session for the handler
    current_user: User = Depends(get_current_user) # Injected current user for the handler
):
    """
    Creates a new blog post with pending status and initiates a background task to generate content.

    Args:
        blog (BlogPostCreate): Blog post data from request.
        background_tasks (BackgroundTasks): Background task manager.
        db (Session, optional): SQLAlchemy database session.
        current_user (User, optional): Current authenticated user.

    Returns:
        BlogPostOut: Newly created blog post data.
    """
    # Create a new blog post entry with a pending status.
    new_blog = BlogPost(title=blog.title, content="", status="pending", owner_id=current_user.id) # Create blog post with pending status
    db.add(new_blog) # Add new blog post to session
    db.commit() # Commit changes
    db.refresh(new_blog) # Refresh the object to get server generated values
    
    # Schedule background task for AI content generation using the new blog writer logic.
    background_tasks.add_task(generate_and_update_blog, new_blog.id, blog.title) # Add a background task for content generation
    
    return new_blog # Return newly created blog post

from app.database import SessionLocal
from app.models import BlogPost
from app.core import ai_agent

def generate_and_update_blog(blog_id: int, topic: str):
    """
    Background task that calls the multi-agent AI blog writer to generate content and updates the blog post.

    Args:
         blog_id (int): Blog post id to update
         topic (str): Blog post topic for AI agent
    """
    # Create a new session for the background task.
    db = SessionLocal() # Create a new DB session
    try: # Use a try-finally block for proper cleanup
        blog = db.query(BlogPost).filter(BlogPost.id == blog_id).first() # Query the blog post with given id
        if not blog: # Check if the blog post exists
            return  # Blog post not found, exit
        try: # Use try except block to catch AI agent errors
            # Call the new blog writer logic; adjust the filename if needed.
            content = ai_agent.write_blog_post(topic, output_file=f"blog_post_{blog_id}.md") # Get the content from AI agent
            if isinstance(content, dict):  # Handle case when agent returns a dictionary
                if "answer" in content: # Check for "answer" key
                    blog.content = content["answer"] # If answer is present set blog content to it
                else:
                    blog.content = str(content) # if there is no answer set blog content to string representation of content
            elif isinstance(content, str): # Handle case when agent returns a string
                 blog.content = content # Set blog content to returned string
            else: # Handle other types with string representation
                blog.content = str(content) # Fallback to string if content type is unknown

            blog.status = "completed"  # Update status to completed
        except Exception as e: # Catch any errors during content generation
            blog.content = f"Error generating content: {str(e)}"  # Set error message in blog content
            blog.status = "failed" # Set status to failed

        db.commit() # Commit changes to DB
    finally: # Always close the DB session
        db.close() # Close the DB session

@router.get(
    "",  # Define GET route to retrieve all blog posts at root path
    response_model=List[BlogPostOut], # Set the expected response model as a List of BlogPostOut
    summary="Retrieve all blog posts", # Provide a summary description
    description="Fetches all blog posts associated with the authenticated user." # Provide detailed description
)
async def get_blog_posts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieves all blog posts for the authenticated user.

    Args:
        db (Session, optional): SQLAlchemy database session.
        current_user (User, optional): Current authenticated user.

    Returns:
        List[BlogPostOut]: List of user's blog posts.
    """
    blogs = db.query(BlogPost).filter(BlogPost.owner_id == current_user.id).all() # Query blog posts for current user
    return blogs # Return the blog posts

@router.get(
    "/{blog_id}", # GET route for retrieving a blog post by id
    response_model=BlogPostOut, # Set the expected response model as BlogPostOut
    summary="Retrieve a single blog post", # Provide a summary description
    description="Fetches a specific blog post by its ID for the authenticated user."  # Provide detailed description
)
async def get_blog_post(blog_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieves a specific blog post by ID for the authenticated user.

    Args:
         blog_id (int): Blog post id to retrieve
        db (Session, optional): SQLAlchemy database session.
        current_user (User, optional): Current authenticated user.

    Returns:
        BlogPostOut: The requested blog post.

    Raises:
        HTTPException: If the blog post not found.
    """
    blog = db.query(BlogPost).filter(BlogPost.id == blog_id, BlogPost.owner_id == current_user.id).first() # Query DB for blog post with given id and owner
    if not blog: # Check if blog post exists
        raise HTTPException(  # Raise exception if blog post doesn't exist
            status_code=status.HTTP_404_NOT_FOUND,  # Set the status code
            detail="Blog post not found" # Provide detailed error message
        )
    return blog # Return the blog post

@router.put(
    "/{blog_id}",  # PUT route for updating the blog post by id
    response_model=BlogPostOut, # Set the expected response model as BlogPostOut
    summary="Update a blog post", # Provide a summary description
    description="Updates the title and/or content of a blog post for the authenticated user." # Provide detailed description
)
async def update_blog_post(blog_id: int, blog_update: BlogPostUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Updates a blog post by ID for the authenticated user.

    Args:
        blog_id (int): Blog post ID to update.
        blog_update (BlogPostUpdate): Updated blog data.
        db (Session, optional): SQLAlchemy database session.
        current_user (User, optional): Current authenticated user.

    Returns:
        BlogPostOut: Updated blog post.

    Raises:
        HTTPException: If the blog post does not exist.
    """
    blog = db.query(BlogPost).filter(BlogPost.id == blog_id, BlogPost.owner_id == current_user.id).first() # Query the blog post with the given id and owner
    if not blog: # Check if the blog post exists
        raise HTTPException( # Raise exception if blog post doesn't exists
            status_code=status.HTTP_404_NOT_FOUND, # Set the status code
            detail="Blog post not found"  # Provide detailed error message
        )
    
    if blog_update.title is not None:  # Update title if provided
        blog.title = blog_update.title
    if blog_update.content is not None:  # Update content if provided
        blog.content = blog_update.content
    
    db.commit() # Commit changes to the DB
    db.refresh(blog) # Refresh the object to get server generated changes
    return blog # Return the blog post

@router.delete(
    "/{blog_id}",  # Define DELETE route to delete blog post
    status_code=status.HTTP_204_NO_CONTENT, # Set the status code
    summary="Delete a blog post", # Provide a summary description
    description="Deletes a blog post by its ID for the authenticated user." # Provide detailed description
)
async def delete_blog_post(blog_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Deletes a blog post by ID for the authenticated user.

    Args:
        blog_id (int): Blog post ID to delete.
        db (Session, optional): SQLAlchemy database session.
        current_user (User, optional): Current authenticated user.

    Raises:
        HTTPException: If the blog post does not exist.
    """
    blog = db.query(BlogPost).filter(BlogPost.id == blog_id, BlogPost.owner_id == current_user.id).first()  # Query the blog post with the given id and user owner
    if not blog: # Check if the blog post exists
        raise HTTPException( # Raise exception if the blog post doesn't exist
            status_code=status.HTTP_404_NOT_FOUND, # Set the status code
            detail="Blog post not found" # Provide detailed error message
        )
    db.delete(blog) # Delete blog post from DB
    db.commit() # Commit the changes
    return # Return empty body