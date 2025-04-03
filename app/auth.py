from fastapi import HTTPException, Depends
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi.security import OAuth2PasswordBearer

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user database (Temporary Fix)
fake_users_db = {
    "admin": {
        "username": "admin",
        "password": pwd_context.hash("password123")  # Default user for testing
    }
}

# Secret key for JWT token signing
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2PasswordBearer for token-based auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Hash a password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Verify a password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Create a JWT access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Extract user from token
def get_current_user(token: str = Depends(oauth2_scheme)):
    print(f"DEBUG: Received token -> {token}")  # Debugging

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        print(f"DEBUG: Decoded username -> {username}")  # Debugging

        if username is None or username not in fake_users_db:
            print("DEBUG: Invalid token detected!")  # Debugging
            raise HTTPException(status_code=401, detail="Invalid token")

        return {"username": username}

    except JWTError as e:
        print(f"DEBUG: JWTError occurred -> {str(e)}")  # Debugging
        raise HTTPException(status_code=401, detail="Invalid authentication")
