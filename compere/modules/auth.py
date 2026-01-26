"""
Authentication module with database-backed user management.
"""

import logging
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .config import get_access_token_expire_minutes, get_secret_key, is_auth_enabled
from .database import get_db
from .models import Token, TokenData, User, UserCreate, UserInDB, UserOut

logger = logging.getLogger(__name__)

router = APIRouter()

# JWT Configuration
ALGORITHM = "HS256"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token security
security = HTTPBearer(auto_error=False)


def _get_secret_key() -> str:
    """Get SECRET_KEY, raising error if not configured."""
    secret_key = get_secret_key()
    if not secret_key:
        raise RuntimeError(
            "SECRET_KEY environment variable is required for authentication. "
            "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
        )
    return secret_key


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def get_user(db: Session, username: str) -> UserInDB | None:
    """Get user from database by username."""
    user = db.query(User).filter(User.username == username).first()
    if user:
        return UserInDB.model_validate(user)
    return None


def get_user_by_email(db: Session, email: str) -> UserInDB | None:
    """Get user from database by email."""
    user = db.query(User).filter(User.email == email).first()
    if user:
        return UserInDB.model_validate(user)
    return None


def authenticate_user(db: Session, username: str, password: str) -> UserInDB | None:
    """Authenticate a user by username and password."""
    user = get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(db: Session, user_create: UserCreate, is_superuser: bool = False) -> User:
    """Create a new user in the database."""
    hashed_password = get_password_hash(user_create.password)
    db_user = User(
        username=user_create.username,
        email=user_create.email,
        full_name=user_create.full_name,
        hashed_password=hashed_password,
        is_superuser=is_superuser,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire_minutes = get_access_token_expire_minutes()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=expire_minutes)

    to_encode.update({"exp": expire})
    secret_key = _get_secret_key()
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> UserInDB:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise credentials_exception

    try:
        secret_key = _get_secret_key()
        payload = jwt.decode(credentials.credentials, secret_key, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        raise credentials_exception from e

    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Get current active user."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def optional_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> UserInDB | None:
    """Optional authentication - returns user if authenticated, None otherwise."""
    if not is_auth_enabled():
        return None

    if credentials is None:
        return None

    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None


def required_auth() -> UserInDB | None:
    """Required authentication dependency."""
    if not is_auth_enabled():
        return None
    return Depends(get_current_active_user)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    username: str,
    password: str,
    db: Session = Depends(get_db),
) -> dict:
    """Login endpoint to get access token."""
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=get_access_token_expire_minutes())
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=UserOut)
async def read_users_me(current_user: UserInDB = Depends(get_current_active_user)) -> UserInDB:
    """Get current user info."""
    return current_user


@router.post("/users/", response_model=UserOut)
async def create_new_user(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserInDB | None = Depends(optional_auth),
) -> User:
    """Create a new user. Only superusers can create users when auth is enabled."""
    # Check if this is the first user (allow creating first admin)
    existing_users = db.query(User).count()

    if existing_users > 0 and is_auth_enabled():
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to create users",
            )
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only superusers can create new users",
            )

    # Check for existing username/email
    if get_user(db, user_create.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    if user_create.email and get_user_by_email(db, user_create.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # First user is automatically a superuser
    is_superuser = existing_users == 0
    if is_superuser:
        logger.info(f"Creating first user '{user_create.username}' as superuser")

    return create_user(db, user_create, is_superuser=is_superuser)
