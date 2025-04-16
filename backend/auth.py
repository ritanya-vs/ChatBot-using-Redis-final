from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import redis
import random
import string
import hashlib
from redis_client import get_redis_connection

# Initialize Redis
redis_client = get_redis_connection()

# Create a router for authentication
router = APIRouter()

# Pydantic model for request validation
class UserCredentials(BaseModel):
    username: str
    password: str

# Helper function to hash passwords securely
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/register")
def register(credentials: UserCredentials):
    """Registers a new user by storing a hashed password in Redis."""
    
    # Check if the username already exists
    if redis_client.hexists("users", credentials.username):
        raise HTTPException(status_code=400, detail="Username already exists")

    # Store hashed password
    hashed_pw = hash_password(credentials.password)
    redis_client.hset("users", credentials.username, hashed_pw)

    return {"message": "User registered successfully"}

@router.post("/login")
def login(credentials: UserCredentials):
    """Authenticates the user and generates a session token."""

    # Fetch stored password hash
    stored_hashed_pw = redis_client.hget("users", credentials.username)

    if not stored_hashed_pw:  # User not found
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if isinstance(stored_hashed_pw, bytes):  # Convert bytes to string
        stored_hashed_pw = stored_hashed_pw.decode()

    # Check password match
    if stored_hashed_pw != hash_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate a session token
    session_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    # Store session in Redis with expiry (e.g., 24 hours)
    redis_client.setex(f"session:{session_token}", 86400, credentials.username)

    return {"session_token": session_token}


def authenticate_user(session_token: str):
    """Validates a session token and returns the associated username."""
    
    if not session_token:
        return None  # No token provided

    username = redis_client.get(f"session:{session_token}")
    
    if username is None:
        return None  # Invalid session token
    
    return username  # Return decoded username
