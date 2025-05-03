from fastapi import Request, HTTPException, status
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from dotenv import load_dotenv
from core.email.utils import dispatch_email, render_template
import os

from users.models import TokenPayload, EmailData
import logging

logging.basicConfig(level=logging.DEBUG)

# --- Environment Settings ---
load_dotenv()
BASE_URL = os.getenv("BASE_URL")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES"))
JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES"))

# Password hashing configuration
crypt_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain password using argon2."""
    try:
        logging.debug(f"Hashing password: {password}")
        hashed = crypt_context.hash(password)
        logging.debug(f"Password hashed successfully: {hashed}")
        return hashed
    except Exception as e:
        logging.error("Error occurred while hashing password:")
        raise ValueError("Error occurred while hashing password: {e}")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that a plain password matches its hashed version.
    """
    try:
        return crypt_context.verify(plain_password, hashed_password)
    except Exception as e:
        logging.error(f"Password verification error: {e}")
        raise ValueError("Invalid password")

def create_access_token(data: dict) -> str:
    try:
        expire = datetime.utcnow() + timedelta(seconds=JWT_ACCESS_TOKEN_EXPIRES)
        # Build the payload using the TokenPayload model
        payload = TokenPayload(
            sub=str(data["sub"]),
            username=data["username"],
            firstname=data["firstname"],
            lastname=data["lastname"],
            email=data["email"],
            exp=expire,
        )
        logging.debug(f"Token payload: {payload.dict()}")
        token = jwt.encode(payload.dict(), JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token
    except Exception as e:
        logging.error(f"JWT generation error: {e}")
        raise

def create_refresh_token(data: dict) -> str:
    """
    Create a refresh token with error handling.
    """
    try:
        expire = datetime.utcnow() + timedelta(seconds=JWT_REFRESH_TOKEN_EXPIRES)
        # Build the payload using the TokenPayload model
        payload = TokenPayload(
            sub=str(data["sub"]),  # Ensure sub is always a string
            username=data["username"],
            firstname=data["firstname"],
            lastname=data["lastname"],
            email=data["email"],
            exp=expire,
        )
        logging.debug(f"Refresh token payload: {payload.dict()}")
        token = jwt.encode(payload.dict(), JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token
    except Exception as e:
        logging.error(f"JWT refresh token generation error: {e}")
        raise ValueError("Failed to generate refresh token")

def decode_token(token: str, token_type: str = "access") -> TokenPayload:
    """
    Decodes and validates a JWT token (access or refresh).
    """
    try:
        # Decode the token
        decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Convert "exp" to datetime
        if "exp" in decoded:
            decoded["exp"] = datetime.fromtimestamp(decoded["exp"])
        
        # Validate the structure using the TokenPayload model
        payload = TokenPayload(**decoded)
        logging.info(f"{token_type.capitalize()} token decoded successfully for user {payload.username}")
        return payload
    except jwt.ExpiredSignatureError:
        logging.error(f"{token_type.capitalize()} token has expired")
        raise ValueError(f"{token_type.capitalize()} token has expired")
    except jwt.InvalidTokenError:
        logging.error(f"Invalid {token_type} token")
        raise ValueError(f"Invalid {token_type} token")
    except ValidationError as e:
        logging.error(f"{token_type.capitalize()} token validation error: {e}")
        raise ValueError(f"Token validation error: {e}")

def construct_link(path: str) -> str:
    """
    Generates an email link using the path.
    """
    return f"{BASE_URL}/{path}"

def send_email(email_data: EmailData):
    """
    Sends an email to the user based on a specified template and provided link.
    """
    # Render HTML email content
    html_body = render_template(f"{email_data.template_name}.html", {
        "username": email_data.username,
        "firstname": email_data.firstname,
        "lastname": email_data.lastname,
        "link": email_data.link, 
    })
    # Send email
    dispatch_email(
        to_email=email_data.to_email,
        subject=email_data.subject,
        html_body=html_body
    )
    
async def get_refresh_token_from_request(request: Request) -> str:
    """Extract refresh token from the request."""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    refresh_token_cookie = request.cookies.get("refresh_token")
    if refresh_token_cookie:
        return refresh_token_cookie
    raise HTTPException(status_code=401, detail="Refresh token is missing")




