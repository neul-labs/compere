from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
import jwt
from jwt import PyJWTError

from .database import get_db
from .models import User, Comparison

router = APIRouter()

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    return {"user_id": user_id}

def rate_limit(max_requests: int, window_seconds: int):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Implement rate limiting logic here
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def check_user_comparison_limit(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = user["user_id"]
    # Check if user has exceeded comparison limit
    comparison_count = db.query(Comparison).filter(
        Comparison.user_id == user_id,
        Comparison.created_at > datetime.utcnow() - timedelta(days=1)
    ).count()
    if comparison_count >= 100:  # Limit of 100 comparisons per day
        raise HTTPException(status_code=429, detail="Comparison limit exceeded")
    return user

@router.post("/token")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.verify_password(password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}