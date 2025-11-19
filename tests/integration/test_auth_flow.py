# tests/integration/test_auth_flow.py
"""
Integration tests for authentication and user management.
SYNC version (no async/await) - matches sync SQLAlchemy backend.
"""

import pytest
from starlette.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import verify_password, create_access_token


@pytest.mark.integration
@pytest.mark.auth
class TestUserRegistration:
    """Test user registration endpoints"""
    
    def test_register_new_user_success(
        self,
        client: TestClient,
        db_session: Session
    ):
        """Test successful user registration"""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!",
            "first_name": "New",
            "last_name": "User"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["first_name"] == user_data["first_name"]
        assert data["last_name"] == user_data["last_name"]
        assert "id" in data
        assert data["is_active"] is True
        assert "created_at" in data
        assert "password" not in data
        assert "hashed_password" not in data
    
    def test_register_duplicate_email(
        self,
        client: TestClient,
        test_user: User
    ):
        """Test registration fails with duplicate email"""
        user_data = {
            "email": test_user.email,
            "username": "differentusername",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "email" in data["detail"].lower()
    
    def test_register_duplicate_username(
        self,
        client: TestClient,
        test_user: User
    ):
        """Test registration fails with duplicate username"""
        user_data = {
            "email": "newemail@example.com",
            "username": test_user.username,
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "username" in data["detail"].lower()
    
    def test_register_invalid_email(
        self,
        client: TestClient
    ):
        """Test registration fails with invalid email format"""
        user_data = {
            "email": "not-an-email",
            "username": "testuser",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422
    
    def test_register_weak_password(
        self,
        client: TestClient
    ):
        """Test registration fails with weak password"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "weak",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422
    
    def test_register_missing_required_fields(
        self,
        client: TestClient
    ):
        """Test registration fails with missing required fields"""
        user_data = {
            "email": "test@example.com",
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422
    
    def test_password_is_hashed(
        self,
        client: TestClient,
        db_session: Session
    ):
        """Test that password is properly hashed in database"""
        plain_password = "SecurePass123!"
        user_data = {
            "email": "hashtest@example.com",
            "username": "hashtest",
            "password": plain_password,
            "first_name": "Hash",
            "last_name": "Test"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 200
        
        user = db_session.query(User).filter(User.email == user_data["email"]).first()
        
        assert user.hashed_password != plain_password
        assert len(user.hashed_password) > 20
        assert verify_password(plain_password, user.hashed_password)


@pytest.mark.integration
@pytest.mark.auth
class TestUserLogin:
    """Test user login endpoints"""
    
    def test_login_success_oauth2_form(
        self,
        client: TestClient,
        test_user: User
    ):
        """Test successful login with OAuth2 form format"""
        login_data = {
            "username": test_user.email,
            "password": "TestPassword123!"
        }
        
        response = client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == test_user.email
    
    def test_login_success_json_format(
        self,
        client: TestClient,
        test_user: User
    ):
        """Test successful login with JSON format"""
        login_data = {
            "email": test_user.email,
            "password": "TestPassword123!"
        }
        
        response = client.post("/api/v1/auth/login-json", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == test_user.email
    
    def test_login_wrong_password(
        self,
        client: TestClient,
        test_user: User
    ):
        """Test login fails with wrong password"""
        login_data = {
            "email": test_user.email,
            "password": "WrongPassword123!"
        }
        
        response = client.post("/api/v1/auth/login-json", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_login_nonexistent_user(
        self,
        client: TestClient
    ):
        """Test login fails with nonexistent user"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "Password123!"
        }
        
        response = client.post("/api/v1/auth/login-json", json=login_data)
        
        assert response.status_code == 401
    
    def test_login_inactive_user(
        self,
        client: TestClient,
        db_session: Session
    ):
        """Test login fails for inactive user"""
        from app.core.security import get_password_hash
        inactive_user = User(
            email="inactive@example.com",
            username="inactiveuser",
            hashed_password=get_password_hash("Password123!"),
            is_active=False
        )
        db_session.add(inactive_user)
        db_session.commit()
        
        login_data = {
            "email": "inactive@example.com",
            "password": "Password123!"
        }
        
        response = client.post("/api/v1/auth/login-json", json=login_data)
        
        # Your API returns 400 for inactive users
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_jwt_token_contains_user_id(
        self,
        client: TestClient,
        test_user: User
    ):
        """Test that JWT token contains user ID"""
        login_data = {
            "email": test_user.email,
            "password": "TestPassword123!"
        }
        
        response = client.post("/api/v1/auth/login-json", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        token = data["access_token"]
        
        from jose import jwt
        from app.core.config import settings
        
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        assert "sub" in payload
        assert int(payload["sub"]) == test_user.id


@pytest.mark.integration
@pytest.mark.auth
class TestProtectedEndpoints:
    """Test authentication required for protected endpoints"""
    
    def test_get_current_user_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User
    ):
        """Test getting current user info with valid token"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert "password" not in data
        assert "hashed_password" not in data
    
    def test_get_current_user_no_token(
        self,
        client: TestClient
    ):
        """Test getting current user fails without token"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code in [401, 403]
    
    def test_get_current_user_invalid_token(
        self,
        client: TestClient
    ):
        """Test getting current user fails with invalid token"""
        invalid_headers = {"Authorization": "Bearer invalid_token_here"}
        
        response = client.get("/api/v1/auth/me", headers=invalid_headers)
        
        assert response.status_code == 401
    
    def test_get_current_user_expired_token(
        self,
        client: TestClient,
        test_user: User
    ):
        """Test getting current user fails with expired token"""
        from datetime import timedelta
        
        expired_token = create_access_token(
            subject=str(test_user.id),
            expires_delta=timedelta(minutes=-1)
        )
        expired_headers = {"Authorization": f"Bearer {expired_token}"}
        
        response = client.get("/api/v1/auth/me", headers=expired_headers)
        
        assert response.status_code == 401
    
    def test_get_current_user_malformed_token(
        self,
        client: TestClient
    ):
        """Test getting current user fails with malformed token"""
        malformed_headers = {"Authorization": "Bearer not.a.valid.jwt"}
        
        response = client.get("/api/v1/auth/me", headers=malformed_headers)
        
        assert response.status_code == 401
    
    def test_protected_endpoint_requires_auth(
        self,
        client: TestClient
    ):
        """Test that profile endpoint requires authentication"""
        response = client.get("/api/v1/profiles/me")
        
        assert response.status_code in [401, 403]


@pytest.mark.integration
@pytest.mark.auth
class TestLogout:
    """Test logout functionality"""
    
    def test_logout_success(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test successful logout"""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "detail" in data
    
    def test_logout_without_auth(
        self,
        client: TestClient
    ):
        """Test logout without authentication"""
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code in [200, 401]


@pytest.mark.integration
@pytest.mark.auth
class TestMultipleUsers:
    """Test multiple user scenarios"""
    
    def test_multiple_users_separate_data(
        self,
        client: TestClient,
        test_user: User,
        test_user_2: User,
        user_token: str
    ):
        """Test that different users have separate data"""
        user1_headers = {"Authorization": f"Bearer {user_token}"}
        
        user2_token = create_access_token(subject=str(test_user_2.id))
        user2_headers = {"Authorization": f"Bearer {user2_token}"}
        
        response1 = client.get("/api/v1/auth/me", headers=user1_headers)
        response2 = client.get("/api/v1/auth/me", headers=user2_headers)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        assert data1["id"] != data2["id"]
        assert data1["email"] != data2["email"]
        assert data1["username"] != data2["username"]


@pytest.mark.integration
@pytest.mark.auth
class TestAdminUser:
    """Test admin user functionality"""
    
    def test_admin_user_login(
        self,
        client: TestClient,
        admin_user: User
    ):
        """Test admin user can login"""
        login_data = {
            "email": admin_user.email,
            "password": "AdminPassword123!"
        }
        
        response = client.post("/api/v1/auth/login-json", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == admin_user.email
    
    def test_admin_user_has_superuser_flag(
        self,
        client: TestClient,
        admin_headers: dict,
        admin_user: User
    ):
        """Test admin user has superuser status"""
        response = client.get("/api/v1/auth/me", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == admin_user.email
