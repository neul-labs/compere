"""
Tests for the authentication module.
"""

import os
import sys
from datetime import timedelta
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient

# Add the compere package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from compere.main import app
from compere.modules.auth import (
    ALGORITHM,
    SECRET_KEY,
    Token,
    TokenData,
    User,
    UserInDB,
    authenticate_user,
    create_access_token,
    fake_users_db,
    get_current_active_user,
    get_current_user,
    get_password_hash,
    get_user,
    optional_auth,
    required_auth,
    verify_password,
)

client = TestClient(app)


class TestPasswordHashing:
    """Test password hashing functions"""

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        hashed = get_password_hash("testpassword")
        assert verify_password("testpassword", hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        hashed = get_password_hash("testpassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_get_password_hash(self):
        """Test password hashing"""
        hashed = get_password_hash("testpassword")
        assert hashed != "testpassword"
        assert len(hashed) > 0


class TestUserDatabase:
    """Test user database functions"""

    def test_get_user_exists(self):
        """Test getting an existing user"""
        user = get_user(fake_users_db, "admin")
        assert user is not None
        assert user.username == "admin"
        assert user.email == "admin@example.com"
        assert isinstance(user, UserInDB)

    def test_get_user_not_exists(self):
        """Test getting a non-existent user"""
        user = get_user(fake_users_db, "nonexistent")
        assert user is None

    def test_get_demo_user(self):
        """Test getting demo user"""
        user = get_user(fake_users_db, "demo")
        assert user is not None
        assert user.username == "demo"
        assert user.full_name == "Demo User"


class TestAuthentication:
    """Test authentication functions"""

    def test_authenticate_user_success(self):
        """Test successful user authentication"""
        user = authenticate_user(fake_users_db, "admin", "admin123")
        assert user is not False
        assert user.username == "admin"

    def test_authenticate_user_wrong_password(self):
        """Test authentication with wrong password"""
        result = authenticate_user(fake_users_db, "admin", "wrongpassword")
        assert result is False

    def test_authenticate_user_nonexistent(self):
        """Test authentication with non-existent user"""
        result = authenticate_user(fake_users_db, "nonexistent", "password")
        assert result is False


class TestTokens:
    """Test JWT token functions"""

    def test_create_access_token_default_expiry(self):
        """Test token creation with default expiry"""
        token = create_access_token(data={"sub": "testuser"})
        assert token is not None
        assert len(token) > 0

    def test_create_access_token_custom_expiry(self):
        """Test token creation with custom expiry"""
        token = create_access_token(data={"sub": "testuser"}, expires_delta=timedelta(hours=1))
        assert token is not None
        assert len(token) > 0

    def test_create_access_token_data_preserved(self):
        """Test that token data is preserved"""
        from jose import jwt

        token = create_access_token(data={"sub": "testuser", "role": "admin"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"
        assert "exp" in payload


class TestCurrentUser:
    """Test get current user functions"""

    def test_get_current_user_valid_token(self):
        """Test getting current user with valid token"""
        token = create_access_token(data={"sub": "admin"})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        user = get_current_user(credentials)
        assert user.username == "admin"

    def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
        assert exc_info.value.status_code == 401

    def test_get_current_user_no_username(self):
        """Test getting current user with token missing username"""
        from jose import jwt

        token = jwt.encode({"data": "test"}, SECRET_KEY, algorithm=ALGORITHM)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
        assert exc_info.value.status_code == 401

    def test_get_current_user_user_not_found(self):
        """Test getting current user when user doesn't exist in DB"""
        token = create_access_token(data={"sub": "nonexistent_user"})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
        assert exc_info.value.status_code == 401


class TestActiveUser:
    """Test active user functions"""

    def test_get_current_active_user_active(self):
        """Test getting active user"""
        user = UserInDB(
            username="test",
            email="test@test.com",
            full_name="Test User",
            disabled=False,
            hashed_password="hash",
        )
        result = get_current_active_user(user)
        assert result.username == "test"

    def test_get_current_active_user_disabled(self):
        """Test getting disabled user raises exception"""
        user = UserInDB(
            username="test",
            email="test@test.com",
            full_name="Test User",
            disabled=True,
            hashed_password="hash",
        )
        with pytest.raises(HTTPException) as exc_info:
            get_current_active_user(user)
        assert exc_info.value.status_code == 400
        assert "Inactive user" in exc_info.value.detail


class TestAuthDependencies:
    """Test authentication dependency functions"""

    def test_optional_auth_disabled(self):
        """Test optional auth when auth is disabled"""
        with patch.dict(os.environ, {"AUTH_ENABLED": "false"}):
            result = optional_auth()
            assert result is None

    def test_required_auth_disabled(self):
        """Test required auth when auth is disabled"""
        with patch.dict(os.environ, {"AUTH_ENABLED": "false"}):
            result = required_auth()
            # Should return a lambda that returns None
            assert callable(result)
            assert result() is None


class TestAuthEndpoints:
    """Test authentication API endpoints"""

    def test_login_success(self):
        """Test successful login"""
        response = client.post("/auth/token", params={"username": "admin", "password": "admin123"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = client.post("/auth/token", params={"username": "admin", "password": "wrongpassword"})
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        response = client.post("/auth/token", params={"username": "nonexistent", "password": "password"})
        assert response.status_code == 401

    def test_get_current_user_endpoint(self):
        """Test /users/me endpoint with valid token"""
        # First login to get token
        login_response = client.post("/auth/token", params={"username": "admin", "password": "admin123"})
        token = login_response.json()["access_token"]

        # Then access protected endpoint
        response = client.get("/auth/users/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["email"] == "admin@example.com"

    def test_get_current_user_no_token(self):
        """Test /users/me endpoint without token"""
        response = client.get("/auth/users/me")
        # FastAPI's HTTPBearer returns 403 when no credentials are provided
        assert response.status_code in [401, 403]  # No credentials provided

    def test_get_current_user_invalid_token(self):
        """Test /users/me endpoint with invalid token"""
        response = client.get("/auth/users/me", headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 401


class TestModels:
    """Test Pydantic models"""

    def test_token_model(self):
        """Test Token model"""
        token = Token(access_token="test_token", token_type="bearer")
        assert token.access_token == "test_token"
        assert token.token_type == "bearer"

    def test_token_data_model(self):
        """Test TokenData model"""
        token_data = TokenData(username="testuser")
        assert token_data.username == "testuser"

        token_data_none = TokenData()
        assert token_data_none.username is None

    def test_user_model(self):
        """Test User model"""
        user = User(username="test", email="test@test.com", full_name="Test User", disabled=False)
        assert user.username == "test"
        assert user.email == "test@test.com"

    def test_user_in_db_model(self):
        """Test UserInDB model"""
        user = UserInDB(
            username="test",
            email="test@test.com",
            full_name="Test User",
            disabled=False,
            hashed_password="hashed_pwd",
        )
        assert user.hashed_password == "hashed_pwd"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
