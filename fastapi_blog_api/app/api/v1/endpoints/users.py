from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.schemas import UserCreate, UserOut, Token
from app.models import User
from app.database import SessionLocal
from app.core import security
from app.core.config import settings

router = APIRouter()

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

@router.post(
    "/register", # Define the POST route for /register
    response_model=UserOut, # Set expected response model for the endpoint
    summary="Register a new user", # Set summary description
    description="Creates a new user with a username and password. Returns the user information excluding the password." # Set detailed description
)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user.

    Args:
        user (UserCreate): The user creation data.
        db (Session, optional): SQLAlchemy database session. Defaults to dependency injection via `get_db`.

    Returns:
        UserOut: The created user data.

    Raises:
        HTTPException: If the username already exists.
    """
    # Check if user exists
    existing_user = db.query(User).filter(User.username == user.username).first() # Check for existing users with the same username
    if existing_user:
        raise HTTPException( # Raise exception if user exists
            status_code=status.HTTP_400_BAD_REQUEST, # Set status code
            detail="Username already registered" # Provide exception message
        )
    hashed_password = security.get_password_hash(user.password) # Get hashed password
    new_user = User(username=user.username, hashed_password=hashed_password) # Create new User model
    db.add(new_user) # Add new user to DB session
    db.commit() # Commit changes
    db.refresh(new_user) # Refresh the new user object
    return new_user # Return new user data

@router.post(
    "/login", # Define the POST route for /login
    response_model=Token, # Set expected response model for the endpoint
    summary="User login", # Set summary description
    description="Authenticates an existing user and returns a JWT token for further requests." # Set detailed description
)
def login(user: UserCreate, db: Session = Depends(get_db)):
    """
    Authenticates a user and returns a JWT token.

    Args:
        user (UserCreate): The user login data.
        db (Session, optional): SQLAlchemy database session. Defaults to dependency injection via `get_db`.

    Returns:
        Token: The authentication token.

    Raises:
        HTTPException: If the credentials are invalid.
    """
    db_user = db.query(User).filter(User.username == user.username).first() # Query for the user using username
    if not db_user or not security.verify_password(user.password, db_user.hashed_password): # Check if user exists and if provided password matches
        raise HTTPException( # Raise exception if user does not exists or password does not match
            status_code=status.HTTP_401_UNAUTHORIZED, # Set status code
            detail="Invalid credentials" # Provide error message
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) # Set access token validity time
    access_token = security.create_access_token( # create the access token
        data={"sub": db_user.username},  # Set token subject
        expires_delta=access_token_expires # Set token validity
    )
    return {"access_token": access_token, "token_type": "bearer"} # Return the generated token