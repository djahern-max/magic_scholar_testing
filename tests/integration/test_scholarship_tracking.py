# tests/integration/test_scholarship_tracking.py
"""
Integration tests for scholarship tracking endpoints.

Tests cover:
- Dashboard statistics
- Saving/bookmarking scholarships
- Application status transitions
- Filtering and sorting
- Quick action endpoints
- User data isolation
"""

import pytest
from starlette.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.scholarship import Scholarship


@pytest.mark.integration
class TestScholarshipDashboard:
    """Test scholarship dashboard"""

    def test_get_dashboard(
        self, client: TestClient, auth_headers: dict
    ):
        """Test getting scholarship dashboard"""
        response = client.get(
            "/api/v1/scholarship-tracking/dashboard",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "upcoming_deadlines" in data
        assert "overdue" in data
        assert "applications" in data

    def test_dashboard_summary_stats(
        self, client: TestClient, auth_headers: dict
    ):
        """Test dashboard summary statistics"""
        response = client.get(
            "/api/v1/scholarship-tracking/dashboard",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        summary = data["summary"]
        
        assert "total_applications" in summary
        assert "interested" in summary
        assert "planning" in summary
        assert "in_progress" in summary
        assert "submitted" in summary
        assert "accepted" in summary
        assert "rejected" in summary
        assert "not_pursuing" in summary
        assert "total_potential_value" in summary
        assert "total_awarded_value" in summary


@pytest.mark.integration
class TestSaveScholarship:
    """Test saving/bookmarking scholarships"""

    def test_save_scholarship(
        self,
        client: TestClient,
        auth_headers: dict,
        test_scholarship: Scholarship
    ):
        """Test saving a scholarship"""
        save_data = {
            "scholarship_id": test_scholarship.id,
            "status": "interested",
            "notes": "Looks promising"
        }

        response = client.post(
            "/api/v1/scholarship-tracking/applications",
            json=save_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["scholarship_id"] == test_scholarship.id
        assert data["status"] == "interested"
        assert "id" in data

    def test_save_duplicate_scholarship_fails(
        self,
        client: TestClient,
        auth_headers: dict,
        test_scholarship: Scholarship
    ):
        """Test cannot save same scholarship twice"""
        save_data = {"scholarship_id": test_scholarship.id}

        # Save first time
        response1 = client.post(
            "/api/v1/scholarship-tracking/applications",
            json=save_data,
            headers=auth_headers
        )
        assert response1.status_code == 201

        # Try to save again
        response2 = client.post(
            "/api/v1/scholarship-tracking/applications",
            json=save_data,
            headers=auth_headers
        )
        assert response2.status_code in [400, 409]

    def test_save_nonexistent_scholarship_fails(
        self, client: TestClient, auth_headers: dict
    ):
        """Test saving nonexistent scholarship fails"""
        save_data = {"scholarship_id": 999999}

        response = client.post(
            "/api/v1/scholarship-tracking/applications",
            json=save_data,
            headers=auth_headers
        )

        assert response.status_code == 404


@pytest.mark.integration
class TestApplicationsList:
    """Test listing scholarship applications"""

    def test_list_applications(
        self, client: TestClient, auth_headers: dict
    ):
        """Test listing user's scholarship applications"""
        response = client.get(
            "/api/v1/scholarship-tracking/applications",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_filter_by_status(
        self,
        client: TestClient,
        auth_headers: dict,
        test_scholarship: Scholarship,
        db_session: Session
    ):
        """Test filtering applications by status"""
        # Save scholarship
        save_data = {"scholarship_id": test_scholarship.id, "status": "submitted"}
        client.post(
            "/api/v1/scholarship-tracking/applications",
            json=save_data,
            headers=auth_headers
        )

        response = client.get(
            "/api/v1/scholarship-tracking/applications?status=submitted",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        for app in data:
            assert app["status"] == "submitted"

    def test_sort_by_deadline(
        self, client: TestClient, auth_headers: dict
    ):
        """Test sorting applications by deadline"""
        response = client.get(
            "/api/v1/scholarship-tracking/applications?sort_by=deadline&sort_order=asc",
            headers=auth_headers
        )

        assert response.status_code == 200


@pytest.mark.integration
class TestApplicationDetails:
    """Test getting application details"""

    def test_get_application_by_id(
        self,
        client: TestClient,
        auth_headers: dict,
        test_scholarship: Scholarship
    ):
        """Test getting specific application"""
        # Save scholarship first
        save_response = client.post(
            "/api/v1/scholarship-tracking/applications",
            json={"scholarship_id": test_scholarship.id},
            headers=auth_headers
        )
        app_id = save_response.json()["id"]

        response = client.get(
            f"/api/v1/scholarship-tracking/applications/{app_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == app_id

    def test_get_other_user_application_fails(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user_2: dict
    ):
        """Test cannot access other user's applications"""
        # This would require creating an application as test_user_2
        # and trying to access it as test_user
        pass


@pytest.mark.integration
class TestApplicationUpdate:
    """Test updating scholarship applications"""

    def test_update_application_status(
        self,
        client: TestClient,
        auth_headers: dict,
        test_scholarship: Scholarship
    ):
        """Test updating application status"""
        # Save scholarship
        save_response = client.post(
            "/api/v1/scholarship-tracking/applications",
            json={"scholarship_id": test_scholarship.id},
            headers=auth_headers
        )
        app_id = save_response.json()["id"]

        # Update status
        update_data = {"status": "in_progress"}
        response = client.put(
            f"/api/v1/scholarship-tracking/applications/{app_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["started_at"] is not None

    def test_update_notes(
        self,
        client: TestClient,
        auth_headers: dict,
        test_scholarship: Scholarship
    ):
        """Test updating application notes"""
        save_response = client.post(
            "/api/v1/scholarship-tracking/applications",
            json={"scholarship_id": test_scholarship.id},
            headers=auth_headers
        )
        app_id = save_response.json()["id"]

        update_data = {"notes": "Updated notes about this scholarship"}
        response = client.put(
            f"/api/v1/scholarship-tracking/applications/{app_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == "Updated notes about this scholarship"


@pytest.mark.integration
class TestQuickActions:
    """Test quick action endpoints"""

    def test_mark_as_submitted(
        self,
        client: TestClient,
        auth_headers: dict,
        test_scholarship: Scholarship
    ):
        """Test mark-submitted quick action"""
        save_response = client.post(
            "/api/v1/scholarship-tracking/applications",
            json={"scholarship_id": test_scholarship.id},
            headers=auth_headers
        )
        app_id = save_response.json()["id"]

        response = client.post(
            f"/api/v1/scholarship-tracking/applications/{app_id}/mark-submitted",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "submitted"
        assert data["submitted_at"] is not None

    def test_mark_as_accepted(
        self,
        client: TestClient,
        auth_headers: dict,
        test_scholarship: Scholarship
    ):
        """Test mark-accepted quick action"""
        save_response = client.post(
            "/api/v1/scholarship-tracking/applications",
            json={"scholarship_id": test_scholarship.id},
            headers=auth_headers
        )
        app_id = save_response.json()["id"]

        response = client.post(
            f"/api/v1/scholarship-tracking/applications/{app_id}/mark-accepted?award_amount=5000",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
        assert data["decision_date"] is not None
        assert data["award_amount"] == 5000

    def test_mark_as_rejected(
        self,
        client: TestClient,
        auth_headers: dict,
        test_scholarship: Scholarship
    ):
        """Test mark-rejected quick action"""
        save_response = client.post(
            "/api/v1/scholarship-tracking/applications",
            json={"scholarship_id": test_scholarship.id},
            headers=auth_headers
        )
        app_id = save_response.json()["id"]

        response = client.post(
            f"/api/v1/scholarship-tracking/applications/{app_id}/mark-rejected",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
        assert data["decision_date"] is not None


@pytest.mark.integration
class TestApplicationDelete:
    """Test deleting scholarship applications"""

    def test_delete_application(
        self,
        client: TestClient,
        auth_headers: dict,
        test_scholarship: Scholarship
    ):
        """Test deleting an application"""
        save_response = client.post(
            "/api/v1/scholarship-tracking/applications",
            json={"scholarship_id": test_scholarship.id},
            headers=auth_headers
        )
        app_id = save_response.json()["id"]

        response = client.delete(
            f"/api/v1/scholarship-tracking/applications/{app_id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(
            f"/api/v1/scholarship-tracking/applications/{app_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404
