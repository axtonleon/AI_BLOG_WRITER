from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Hashes a given password using bcrypt.

    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against its hashed version.

    Args:
        plain_password (str): The plain password.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Creates a JWT access token.

    Args:
        data (dict): The payload data to include in the token.
        expires_delta (Optional[timedelta]): The time duration the token is valid for.

    Returns:
        str: The JWT access token.
    """
    to_encode = data.copy() # Copy to prevent modifying original
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)) # Calculate expiration
    to_encode.update({"exp": expire}) # Set expiration claim
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM) # Encode and return the token

def decode_access_token(token: str):
    """
    Decodes a JWT access token.

    Args:
        token (str): The JWT token to decode.

    Returns:
        Optional[dict]: The decoded payload if successful, otherwise None.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]) # decode the token using JWT
        return payload # return payload if the token is ok
    except jwt.JWTError: # Catch potential JWT errors
        return None # Return None if there was a error decoding the token