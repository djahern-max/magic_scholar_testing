# tests/integration/test_college_tracking.py
"""
Integration tests for college application tracking endpoints.

Tests cover:
- Dashboard statistics
- Saving/bookmarking colleges
- Application types and status transitions
- Filtering and sorting
- Quick action endpoints (including waitlist)
- Decision date tracking
- Fee waiver management
"""

import pytest
from starlette.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.institution import Institution


@pytest.mark.integration
class TestCollegeDashboard:
    """Test college application dashboard"""

    def test_get_dashboard(
        self, client: TestClient, auth_headers: dict
    ):
        """Test getting college dashboard"""
        response = client.get(
            "/api/v1/college-tracking/dashboard",
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
            "/api/v1/college-tracking/dashboard",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        summary = data["summary"]
        
        assert "total_applications" in summary
        assert "submitted" in summary
        assert "in_progress" in summary
        assert "accepted" in summary
        assert "waitlisted" in summary
        assert "rejected" in summary
        assert "awaiting_decision" in summary


@pytest.mark.integration
class TestSaveCollege:
    """Test saving/bookmarking colleges"""

    def test_save_college(
        self,
        client: TestClient,
        auth_headers: dict,
        test_institution: Institution
    ):
        """Test saving a college"""
        save_data = {
            "institution_id": test_institution.id,
            "status": "researching",
            "application_type": "regular_decision",
            "deadline": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
            "notes": "Interested in CS program"
        }

        response = client.post(
            "/api/v1/college-tracking/applications",
            json=save_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["institution_id"] == test_institution.id
        assert data["status"] == "researching"
        assert data["application_type"] == "regular_decision"
        assert "id" in data

    def test_save_duplicate_college_fails(
        self,
        client: TestClient,
        auth_headers: dict,
        test_institution: Institution
    ):
        """Test cannot save same college twice"""
        save_data = {"institution_id": test_institution.id}

        # Save first time
        response1 = client.post(
            "/api/v1/college-tracking/applications",
            json=save_data,
            headers=auth_headers
        )
        assert response1.status_code == 201

        # Try to save again
        response2 = client.post(
            "/api/v1/college-tracking/applications",
            json=save_data,
            headers=auth_headers
        )
        assert response2.status_code in [400, 409]

    def test_save_with_application_types(
        self,
        client: TestClient,
        auth_headers: dict,
        test_institution: Institution
    ):
        """Test saving with different application types"""
        app_types = ["early_decision", "early_action", "regular_decision", "rolling"]
        
        for app_type in app_types:
            save_data = {
                "institution_id": test_institution.id,
                "application_type": app_type
            }
            
            response = client.post(
                "/api/v1/college-tracking/applications",
                json=save_data,
                headers=auth_headers
            )
            
            # First one succeeds, rest fail due to duplicate
            if app_type == "early_decision":
                assert response.status_code == 201
                assert response.json()["application_type"] == app_type
            
            # Clean up for next iteration if needed
            if response.status_code == 201:
                app_id = response.json()["id"]
                client.delete(
                    f"/api/v1/college-tracking/applications/{app_id}",
                    headers=auth_headers
                )


@pytest.mark.integration
class TestApplicationsList:
    """Test listing college applications"""

    def test_list_applications(
        self, client: TestClient, auth_headers: dict
    ):
        """Test listing user's college applications"""
        response = client.get(
            "/api/v1/college-tracking/applications",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_filter_by_status(
        self,
        client: TestClient,
        auth_headers: dict,
        test_institution: Institution
    ):
        """Test filtering applications by status"""
        # Save college
        save_data = {
            "institution_id": test_institution.id,
            "status": "submitted"
        }
        client.post(
            "/api/v1/college-tracking/applications",
            json=save_data,
            headers=auth_headers
        )

        response = client.get(
            "/api/v1/college-tracking/applications?status=submitted",
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
            "/api/v1/college-tracking/applications?sort_by=deadline&sort_order=asc",
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
        test_institution: Institution
    ):
        """Test getting specific application"""
        save_response = client.post(
            "/api/v1/college-tracking/applications",
            json={"institution_id": test_institution.id},
            headers=auth_headers
        )
        app_id = save_response.json()["id"]

        response = client.get(
            f"/api/v1/college-tracking/applications/{app_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == app_id
        assert "institution" in data


@pytest.mark.integration
class TestApplicationUpdate:
    """Test updating college applications"""

    def test_update_application_status(
        self,
        client: TestClient,
        auth_headers: dict,
        test_institution: Institution
    ):
        """Test updating application status"""
        save_response = client.post(
            "/api/v1/college-tracking/applications",
            json={"institution_id": test_institution.id},
            headers=auth_headers
        )
        app_id = save_response.json()["id"]

        update_data = {"status": "in_progress"}
        response = client.put(
            f"/api/v1/college-tracking/applications/{app_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["started_at"] is not None

    def test_update_decision_dates(
        self,
        client: TestClient,
        auth_headers: dict,
        test_institution: Institution
    ):
        """Test updating decision dates"""
        save_response = client.post(
            "/api/v1/college-tracking/applications",
            json={"institution_id": test_institution.id},
            headers=auth_headers
        )
        app_id = save_response.json()["id"]

        update_data = {
            "decision_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "actual_decision_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        response = client.put(
            f"/api/v1/college-tracking/applications/{app_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["decision_date"] is not None
        assert data["actual_decision_date"] is not None

    def test_update_fee_waiver(
        self,
        client: TestClient,
        auth_headers: dict,
        test_institution: Institution
    ):
        """Test updating fee waiver information"""
        save_response = client.post(
            "/api/v1/college-tracking/applications",
            json={"institution_id": test_institution.id},
            headers=auth_headers
        )
        app_id = save_response.json()["id"]

        update_data = {
            "application_fee": 75,
            "fee_waiver_obtained": True
        }
        
        response = client.put(
            f"/api/v1/college-tracking/applications/{app_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["application_fee"] == 75
        assert data["fee_waiver_obtained"] is True

    def test_update_portal_info(
        self,
        client: TestClient,
        auth_headers: dict,
        test_institution: Institution
    ):
        """Test updating portal information"""
        save_response = client.post(
            "/api/v1/college-tracking/applications",
            json={"institution_id": test_institution.id},
            headers=auth_headers
        )
        app_id = save_response.json()["id"]

        update_data = {
            "application_portal": "Common App",
            "portal_url": "https://commonapp.org",
            "portal_username": "testuser123"
        }
        
        response = client.put(
            f"/api/v1/college-tracking/applications/{app_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["application_portal"] == "Common App"
        assert data["portal_url"] == "https://commonapp.org"


@pytest.mark.integration
class TestQuickActions:
    """Test quick action endpoints"""

    def test_mark_as_submitted(
        self,
        client: TestClient,
        auth_headers: dict,
        test_institution: Institution
    ):
        """Test mark-submitted quick action"""
        save_response = client.post(
            "/api/v1/college-tracking/applications",
            json={"institution_id": test_institution.id},
            headers=auth_headers
        )
        app_id = save_response.json()["id"]

        response = client.post(
            f"/api/v1/college-tracking/applications/{app_id}/mark-submitted",
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
        test_institution: Institution
    ):
        """Test mark-accepted quick action"""
        save_response = client.post(
            "/api/v1/college-tracking/applications",
            json={"institution_id": test_institution.id},
            headers=auth_headers
        )
        app_id = save_response.json()["id"]

        response = client.post(
            f"/api/v1/college-tracking/applications/{app_id}/mark-accepted",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
        assert data["decided_at"] is not None

    def test_mark_as_rejected(
        self,
        client: TestClient,
        auth_headers: dict,
        test_institution: Institution
    ):
        """Test mark-rejected quick action"""
        save_response = client.post(
            "/api/v1/college-tracking/applications",
            json={"institution_id": test_institution.id},
            headers=auth_headers
        )
        app_id = save_response.json()["id"]

        response = client.post(
            f"/api/v1/college-tracking/applications/{app_id}/mark-rejected",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
        assert data["decided_at"] is not None

    def test_mark_as_waitlisted(
        self,
        client: TestClient,
        auth_headers: dict,
        test_institution: Institution
    ):
        """Test mark-waitlisted quick action"""
        save_response = client.post(
            "/api/v1/college-tracking/applications",
            json={"institution_id": test_institution.id},
            headers=auth_headers
        )
        app_id = save_response.json()["id"]

        response = client.post(
            f"/api/v1/college-tracking/applications/{app_id}/mark-waitlisted",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "waitlisted"
        assert data["decided_at"] is not None


@pytest.mark.integration
class TestApplicationDelete:
    """Test deleting college applications"""

    def test_delete_application(
        self,
        client: TestClient,
        auth_headers: dict,
        test_institution: Institution
    ):
        """Test deleting an application"""
        save_response = client.post(
            "/api/v1/college-tracking/applications",
            json={"institution_id": test_institution.id},
            headers=auth_headers
        )
        app_id = save_response.json()["id"]

        response = client.delete(
            f"/api/v1/college-tracking/applications/{app_id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(
            f"/api/v1/college-tracking/applications/{app_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404


@pytest.mark.integration
class TestStatusTransitions:
    """Test application status transition logic"""

    def test_status_transition_timestamps(
        self,
        client: TestClient,
        auth_headers: dict,
        test_institution: Institution
    ):
        """Test that status transitions update correct timestamps"""
        save_response = client.post(
            "/api/v1/college-tracking/applications",
            json={"institution_id": test_institution.id},
            headers=auth_headers
        )
        app_id = save_response.json()["id"]

        # Move to in_progress
        response1 = client.put(
            f"/api/v1/college-tracking/applications/{app_id}",
            json={"status": "in_progress"},
            headers=auth_headers
        )
        assert response1.json()["started_at"] is not None

        # Move to submitted
        response2 = client.put(
            f"/api/v1/college-tracking/applications/{app_id}",
            json={"status": "submitted"},
            headers=auth_headers
        )
        assert response2.json()["submitted_at"] is not None

        # Move to accepted
        response3 = client.put(
            f"/api/v1/college-tracking/applications/{app_id}",
            json={"status": "accepted"},
            headers=auth_headers
        )
        assert response3.json()["decided_at"] is not None
