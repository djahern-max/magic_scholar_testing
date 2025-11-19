# tests/conftest.py
"""
Shared test fixtures and configuration for MagicScholar backend tests.
Configured for SYNC SQLAlchemy (not async).
"""

import pytest
from typing import Generator, Dict, Any
from starlette.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta
import os
from decimal import Decimal

from app.main import app
from app.core.database import get_db, Base
from app.core.security import create_access_token, get_password_hash
from app.models.user import User
from app.models.profile import UserProfile
from app.models.institution import Institution, ControlType
from app.models.scholarship import Scholarship


# ===========================
# TEST DATABASE CONFIGURATION
# ===========================

TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:@localhost:5432/magicscholar_test"
)

test_engine = create_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# ===========================
# DATABASE FIXTURES
# ===========================


@pytest.fixture(scope="function", autouse=True)
def setup_test_database():
    """Create all tables before each test and drop them after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Provide a database session for each test with automatic rollback."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Provide a test client for API endpoints."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ===========================
# AUTHENTICATION FIXTURES
# ===========================


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
        hashed_password=get_password_hash("TestPassword123!"),
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_2(db_session: Session) -> User:
    """Create a second test user."""
    user = User(
        email="test2@example.com",
        username="testuser2",
        first_name="Test",
        last_name="User2",
        hashed_password=get_password_hash("TestPassword123!"),
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session: Session) -> User:
    """Create an admin user."""
    user = User(
        email="admin@example.com",
        username="adminuser",
        first_name="Admin",
        last_name="User",
        hashed_password=get_password_hash("AdminPassword123!"),
        is_active=True,
        is_superuser=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_token(test_user: User) -> str:
    """Generate JWT token for test user."""
    return create_access_token(subject=str(test_user.id))


@pytest.fixture
def admin_token(admin_user: User) -> str:
    """Generate JWT token for admin user."""
    return create_access_token(subject=str(admin_user.id))


@pytest.fixture
def auth_headers(user_token: str) -> Dict[str, str]:
    """Auth headers with Bearer token for regular user."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> Dict[str, str]:
    """Auth headers with Bearer token for admin user."""
    return {"Authorization": f"Bearer {admin_token}"}


# ===========================
# DATA FIXTURES
# ===========================


@pytest.fixture
def test_profile(db_session: Session, test_user: User) -> UserProfile:
    """Create a test user profile."""
    profile = UserProfile(
        user_id=test_user.id,
        high_school="Test High School",
        graduation_year=2025,
        gpa=3.8,
        sat_score=1400,
        act_score=32,
        intended_major="Computer Science",
        state="MA",
        city="Boston",
        zip_code="02101",
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile


@pytest.fixture
def test_institution(db_session: Session) -> Institution:
    """Create a test institution (MIT)."""
    institution = Institution(
        ipeds_id=166027,  # MIT's real IPEDS ID
        name="Massachusetts Institute of Technology",
        city="Cambridge",
        state="MA",
        control_type=ControlType.PRIVATE_NONPROFIT,
        student_faculty_ratio=Decimal("3.0"),
        size_category="Medium",
        locale="City: Large",
    )
    db_session.add(institution)
    db_session.commit()
    db_session.refresh(institution)
    return institution


@pytest.fixture
def test_scholarship(db_session: Session) -> Scholarship:
    """Create a test scholarship."""
    scholarship = Scholarship(
        title="Test STEM Scholarship",
        organization="Test Foundation",
        scholarship_type="stem",  # Must be one of the ScholarshipType enum values
        amount_min=5000,
        amount_max=10000,
        deadline=datetime.now() + timedelta(days=60),
        description="Scholarship for STEM students",
        status="active",  # Default but explicit
        difficulty_level="moderate",  # Default but explicit
        is_renewable=False,
    )
    db_session.add(scholarship)
    db_session.commit()
    db_session.refresh(scholarship)
    return scholarship
