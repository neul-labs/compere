"""
Tests for the authentication module.
"""

import os
import sys
from datetime import timedelta

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the compere package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(scope="module")
def auth_test_env():
    """Set up auth test environment with SECRET_KEY."""
    # Save original env
    original_secret = os.environ.get("SECRET_KEY")
    original_auth = os.environ.get("AUTH_ENABLED")

    # Set test env
    os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-32chars"
    os.environ["AUTH_ENABLED"] = "true"

    # Clear config cache to pick up new env vars
    import compere.modules.config as config_module

    config_module.get_config.cache_clear()
    config_module._config = None

    yield

    # Restore original env
    if original_secret is not None:
        os.environ["SECRET_KEY"] = original_secret
    else:
        os.environ.pop("SECRET_KEY", None)

    if original_auth is not None:
        os.environ["AUTH_ENABLED"] = original_auth
    else:
        os.environ.pop("AUTH_ENABLED", None)

    # Clear config cache again
    config_module.get_config.cache_clear()
    config_module._config = None


@pytest.fixture
def auth_db_session(auth_test_env):
    """Create a database session using the auth test database."""
    # Use a separate test database for auth tests
    test_db_url = "sqlite:///./test_auth.db"
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    from compere.modules.database import Base

    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Cleanup
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("./test_auth.db"):
            os.remove("./test_auth.db")


@pytest.fixture
def test_user(auth_db_session):
    """Create a test user."""
    from compere.modules.auth import create_user
    from compere.modules.models import UserCreate

    user_create = UserCreate(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        password="testpassword123",
    )
    user = create_user(auth_db_session, user_create, is_superuser=True)
    return user


class TestPasswordHashing:
    """Test password hashing functions"""

    def test_verify_password_correct(self, auth_test_env):
        """Test password verification with correct password"""
        from compere.modules.auth import get_password_hash, verify_password

        hashed = get_password_hash("testpassword")
        assert verify_password("testpassword", hashed) is True

    def test_verify_password_incorrect(self, auth_test_env):
        """Test password verification with incorrect password"""
        from compere.modules.auth import get_password_hash, verify_password

        hashed = get_password_hash("testpassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_get_password_hash(self, auth_test_env):
        """Test password hashing"""
        from compere.modules.auth import get_password_hash

        hashed = get_password_hash("testpassword")
        assert hashed != "testpassword"
        assert len(hashed) > 0


class TestUserDatabase:
    """Test user database functions"""

    def test_get_user_exists(self, auth_db_session, test_user):
        """Test getting an existing user"""
        from compere.modules.auth import get_user
        from compere.modules.models import UserInDB

        user = get_user(auth_db_session, "testuser")
        assert user is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert isinstance(user, UserInDB)

    def test_get_user_not_exists(self, auth_db_session):
        """Test getting a non-existent user"""
        from compere.modules.auth import get_user

        user = get_user(auth_db_session, "nonexistent")
        assert user is None

    def test_create_user(self, auth_db_session):
        """Test creating a user"""
        from compere.modules.auth import create_user
        from compere.modules.models import UserCreate

        user_create = UserCreate(
            username="newuser",
            email="new@example.com",
            full_name="New User",
            password="newpassword",
        )
        user = create_user(auth_db_session, user_create)
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.hashed_password != "newpassword"  # Password should be hashed


class TestAuthentication:
    """Test authentication functions"""

    def test_authenticate_user_success(self, auth_db_session, test_user):
        """Test successful user authentication"""
        from compere.modules.auth import authenticate_user

        user = authenticate_user(auth_db_session, "testuser", "testpassword123")
        assert user is not None
        assert user.username == "testuser"

    def test_authenticate_user_wrong_password(self, auth_db_session, test_user):
        """Test authentication with wrong password"""
        from compere.modules.auth import authenticate_user

        result = authenticate_user(auth_db_session, "testuser", "wrongpassword")
        assert result is None

    def test_authenticate_user_nonexistent(self, auth_db_session):
        """Test authentication with non-existent user"""
        from compere.modules.auth import authenticate_user

        result = authenticate_user(auth_db_session, "nonexistent", "password")
        assert result is None


class TestTokens:
    """Test JWT token functions"""

    def test_create_access_token_default_expiry(self, auth_test_env):
        """Test token creation with default expiry"""
        from compere.modules.auth import create_access_token

        token = create_access_token(data={"sub": "testuser"})
        assert token is not None
        assert len(token) > 0

    def test_create_access_token_custom_expiry(self, auth_test_env):
        """Test token creation with custom expiry"""
        from compere.modules.auth import create_access_token

        token = create_access_token(data={"sub": "testuser"}, expires_delta=timedelta(hours=1))
        assert token is not None
        assert len(token) > 0

    def test_create_access_token_data_preserved(self, auth_test_env):
        """Test that token data is preserved"""
        from jose import jwt

        from compere.modules.auth import ALGORITHM, create_access_token
        from compere.modules.config import get_secret_key

        token = create_access_token(data={"sub": "testuser", "role": "admin"})
        secret_key = get_secret_key()
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"
        assert "exp" in payload


class TestActiveUser:
    """Test active user functions"""

    def test_get_current_active_user_active(self, auth_test_env):
        """Test getting active user"""
        from compere.modules.auth import get_current_active_user
        from compere.modules.models import UserInDB

        user = UserInDB(
            id=1,
            username="test",
            email="test@test.com",
            full_name="Test User",
            disabled=False,
            is_superuser=False,
            hashed_password="hash",
        )
        result = get_current_active_user(user)
        assert result.username == "test"

    def test_get_current_active_user_disabled(self, auth_test_env):
        """Test getting disabled user raises exception"""
        from compere.modules.auth import get_current_active_user
        from compere.modules.models import UserInDB

        user = UserInDB(
            id=1,
            username="test",
            email="test@test.com",
            full_name="Test User",
            disabled=True,
            is_superuser=False,
            hashed_password="hash",
        )
        with pytest.raises(HTTPException) as exc_info:
            get_current_active_user(user)
        assert exc_info.value.status_code == 400
        assert "Inactive user" in exc_info.value.detail


class TestAuthEndpoints:
    """Test authentication API endpoints using the main app."""

    @pytest.fixture
    def client(self, auth_test_env):
        """Create a test client for auth endpoint tests."""
        from sqlalchemy.orm import sessionmaker

        from compere.main import app
        from compere.modules.database import engine
        from compere.modules.models import User

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        try:
            db.query(User).delete()
            db.commit()
        finally:
            db.close()

        return TestClient(app)

    def test_create_first_user(self, client):
        """Test creating the first user (becomes superuser)"""
        # Use unique username to avoid conflicts
        import uuid

        unique_name = f"firstuser_{uuid.uuid4().hex[:8]}"
        response = client.post(
            "/auth/users/",
            json={
                "username": unique_name,
                "email": f"{unique_name}@example.com",
                "full_name": "First User",
                "password": "firstpassword",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == unique_name

    def test_login_and_get_user(self, client):
        """Test login and accessing protected endpoint"""
        import uuid

        unique_name = f"loginuser_{uuid.uuid4().hex[:8]}"

        # Create a user
        create_response = client.post(
            "/auth/users/",
            json={
                "username": unique_name,
                "email": f"{unique_name}@example.com",
                "full_name": "Login User",
                "password": "loginpassword123",
            },
        )
        assert create_response.status_code == 200

        # Login
        login_response = client.post("/auth/token", params={"username": unique_name, "password": "loginpassword123"})
        assert login_response.status_code == 200
        data = login_response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # Access protected endpoint
        token = data["access_token"]
        me_response = client.get("/auth/users/me", headers={"Authorization": f"Bearer {token}"})
        assert me_response.status_code == 200
        assert me_response.json()["username"] == unique_name

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post("/auth/token", params={"username": "nonexistent", "password": "wrongpassword"})
        assert response.status_code == 401

    def test_get_current_user_no_token(self, client):
        """Test /users/me endpoint without token"""
        response = client.get("/auth/users/me")
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client):
        """Test /users/me endpoint with invalid token"""
        response = client.get("/auth/users/me", headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 401


class TestModels:
    """Test Pydantic models"""

    def test_token_model(self):
        """Test Token model"""
        from compere.modules.models import Token

        token = Token(access_token="test_token", token_type="bearer")
        assert token.access_token == "test_token"
        assert token.token_type == "bearer"

    def test_token_data_model(self):
        """Test TokenData model"""
        from compere.modules.models import TokenData

        token_data = TokenData(username="testuser")
        assert token_data.username == "testuser"

        token_data_none = TokenData()
        assert token_data_none.username is None

    def test_user_out_model(self):
        """Test UserOut model"""
        from compere.modules.models import UserOut

        user = UserOut(
            id=1,
            username="test",
            email="test@test.com",
            full_name="Test User",
            disabled=False,
            is_superuser=False,
        )
        assert user.username == "test"
        assert user.email == "test@test.com"

    def test_user_in_db_model(self):
        """Test UserInDB model"""
        from compere.modules.models import UserInDB

        user = UserInDB(
            id=1,
            username="test",
            email="test@test.com",
            full_name="Test User",
            disabled=False,
            is_superuser=False,
            hashed_password="hashed_pwd",
        )
        assert user.hashed_password == "hashed_pwd"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
