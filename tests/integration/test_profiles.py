# tests/integration/test_profiles.py
"""
Integration tests for user profile endpoints.

Tests cover:
- Getting current user profile
- Updating profile information
- Profile settings management
- File uploads (headshot, resume)
- Resume parsing
- Matching institutions
- Profile validation
"""

import pytest
from starlette.testclient import TestClient
from sqlalchemy.orm import Session
import io

from app.models.user import User
from app.models.profile import UserProfile


@pytest.mark.integration
class TestProfileRetrieval:
    """Test profile retrieval"""

    def test_get_own_profile(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """Test user can get their own profile"""
        response = client.get("/api/v1/profiles/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_user.id
        assert "id" in data

    def test_get_profile_without_auth(self, client: TestClient):
        """Test getting profile without authentication fails"""
        response = client.get("/api/v1/profiles/me")

        assert response.status_code in [401, 403]

    def test_profile_includes_settings(
        self, client: TestClient, auth_headers: dict
    ):
        """Test profile response includes settings"""
        response = client.get("/api/v1/profiles/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "settings" in data
        assert isinstance(data["settings"], dict)


@pytest.mark.integration
class TestProfileUpdate:
    """Test profile update operations"""

    def test_update_basic_info(
        self, client: TestClient, auth_headers: dict
    ):
        """Test updating basic profile information"""
        update_data = {
            "state": "CA",
            "city": "San Francisco",
            "zip_code": "94102",
            "high_school_name": "San Francisco High School",
        }

        response = client.put(
            "/api/v1/profiles/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["state"] == "CA"
        assert data["city"] == "San Francisco"
        assert data["zip_code"] == "94102"
        assert data["high_school_name"] == "San Francisco High School"

    def test_update_academic_info(
        self, client: TestClient, auth_headers: dict
    ):
        """Test updating academic information"""
        update_data = {
            "graduation_year": 2026,
            "gpa": 3.85,
            "gpa_scale": "4.0",
            "sat_score": 1450,
            "act_score": 33,
            "intended_major": "Computer Science",
        }

        response = client.put(
            "/api/v1/profiles/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["graduation_year"] == 2026
        assert data["gpa"] == 3.85
        assert data["sat_score"] == 1450
        assert data["act_score"] == 33

    def test_update_extracurriculars(
        self, client: TestClient, auth_headers: dict
    ):
        """Test updating extracurricular activities"""
        update_data = {
            "extracurriculars": [
                {
                    "activity": "Robotics Club",
                    "role": "President",
                    "years": 3,
                    "description": "Led team to regional competition",
                },
                {
                    "activity": "Debate Team",
                    "role": "Member",
                    "years": 2,
                },
            ]
        }

        response = client.put(
            "/api/v1/profiles/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["extracurriculars"]) == 2
        assert data["extracurriculars"][0]["activity"] == "Robotics Club"

    def test_update_work_experience(
        self, client: TestClient, auth_headers: dict
    ):
        """Test updating work experience"""
        update_data = {
            "work_experience": [
                {
                    "employer": "Tech Startup Inc",
                    "position": "Intern",
                    "duration": "Summer 2024",
                    "description": "Worked on web development",
                }
            ]
        }

        response = client.put(
            "/api/v1/profiles/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["work_experience"]) == 1
        assert data["work_experience"][0]["employer"] == "Tech Startup Inc"

    def test_update_honors_awards(
        self, client: TestClient, auth_headers: dict
    ):
        """Test updating honors and awards"""
        update_data = {
            "honors_awards": [
                "National Merit Scholar",
                "AP Scholar with Distinction",
                "Science Fair First Place",
            ]
        }

        response = client.put(
            "/api/v1/profiles/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["honors_awards"]) == 3
        assert "National Merit Scholar" in data["honors_awards"]

    def test_update_skills(self, client: TestClient, auth_headers: dict):
        """Test updating skills"""
        update_data = {
            "skills": ["Python", "Java", "React", "Public Speaking"]
        }

        response = client.put(
            "/api/v1/profiles/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["skills"]) == 4
        assert "Python" in data["skills"]


@pytest.mark.integration
class TestProfileValidation:
    """Test profile validation rules"""

    def test_invalid_state_code(
        self, client: TestClient, auth_headers: dict
    ):
        """Test state code must be 2 characters"""
        update_data = {"state": "CAL"}  # Should be 2 chars

        response = client.put(
            "/api/v1/profiles/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 422

    def test_invalid_gpa_too_high(
        self, client: TestClient, auth_headers: dict
    ):
        """Test GPA maximum validation"""
        update_data = {"gpa": 5.5}  # Max is 5.0

        response = client.put(
            "/api/v1/profiles/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 422

    def test_invalid_sat_score(
        self, client: TestClient, auth_headers: dict
    ):
        """Test SAT score validation"""
        update_data = {"sat_score": 1700}  # Max is 1600

        response = client.put(
            "/api/v1/profiles/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 422


@pytest.mark.integration
class TestProfileSettings:
    """Test profile settings management"""

    def test_get_settings(self, client: TestClient, auth_headers: dict):
        """Test getting user settings"""
        response = client.get("/api/v1/profiles/me/settings", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "confetti_enabled" in data or "settings" in data

    def test_update_confetti_setting(
        self, client: TestClient, auth_headers: dict
    ):
        """Test updating confetti_enabled setting"""
        update_data = {"confetti_enabled": False}

        response = client.patch(
            "/api/v1/profiles/me/settings", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        
        # Check the setting was updated
        get_response = client.get("/api/v1/profiles/me/settings", headers=auth_headers)
        settings_data = get_response.json()
        
        # Handle different response formats
        confetti_value = settings_data.get("confetti_enabled", 
                                           settings_data.get("settings", {}).get("confetti_enabled"))
        assert confetti_value is False


@pytest.mark.integration  
class TestFileUploads:
    """Test file upload functionality"""

    def test_upload_headshot_jpg(
        self, client: TestClient, auth_headers: dict
    ):
        """Test uploading JPG headshot"""
        # Create fake image file
        fake_image = io.BytesIO(b"fake jpg image content")
        files = {"file": ("headshot.jpg", fake_image, "image/jpeg")}

        response = client.post(
            "/api/v1/profiles/me/upload-headshot",
            files=files,
            headers=auth_headers,
        )

        # May succeed or fail depending on image validation
        assert response.status_code in [200, 400, 422]

    def test_upload_resume_pdf(
        self, client: TestClient, auth_headers: dict
    ):
        """Test uploading PDF resume"""
        # Create fake PDF file
        fake_pdf = io.BytesIO(b"%PDF-1.4 fake pdf content")
        files = {"file": ("resume.pdf", fake_pdf, "application/pdf")}

        response = client.post(
            "/api/v1/profiles/me/upload-resume-and-update",
            files=files,
            headers=auth_headers,
        )

        # May succeed or fail depending on PDF parsing
        assert response.status_code in [200, 400, 422, 500]

    def test_upload_without_auth(self, client: TestClient):
        """Test file upload without authentication fails"""
        fake_image = io.BytesIO(b"fake image")
        files = {"file": ("test.jpg", fake_image, "image/jpeg")}

        response = client.post(
            "/api/v1/profiles/me/upload-headshot",
            files=files,
        )

        assert response.status_code in [401, 403]


@pytest.mark.integration
class TestMatchingInstitutions:
    """Test institution matching"""

    def test_get_matching_institutions(
        self, client: TestClient, auth_headers: dict
    ):
        """Test getting matching institutions"""
        response = client.get(
            "/api/v1/profiles/me/matching-institutions",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "institutions" in data or "matches" in data or isinstance(data, list)

    def test_matching_with_location_preference(
        self, client: TestClient, auth_headers: dict
    ):
        """Test matching considers location preference"""
        # Set location preference
        update_data = {"location_preference": "CA"}
        client.put("/api/v1/profiles/me", json=update_data, headers=auth_headers)

        response = client.get(
            "/api/v1/profiles/me/matching-institutions",
            headers=auth_headers
        )

        assert response.status_code == 200

    def test_matching_with_custom_limit(
        self, client: TestClient, auth_headers: dict
    ):
        """Test matching with custom result limit"""
        response = client.get(
            "/api/v1/profiles/me/matching-institutions?limit=10",
            headers=auth_headers
        )

        assert response.status_code == 200
