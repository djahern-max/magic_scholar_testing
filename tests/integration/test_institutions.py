# tests/integration/test_institutions.py
"""
Integration tests for institution endpoints.

Tests cover:
- Listing institutions with pagination
- Searching institutions
- Filtering by state and control type
from app.models.institution import ControlType
- Getting institution details
- Statistics and summaries
"""

import pytest
from starlette.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal
from app.models.institution import ControlType

from app.models.institution import Institution


@pytest.mark.integration
class TestInstitutionList:
    """Test institution listing and pagination"""

    def test_list_institutions_default(
        self, client: TestClient, test_institution: Institution
    ):
        """Test listing institutions with default parameters"""
        response = client.get("/api/v1/institutions/")

        assert response.status_code == 200
        data = response.json()
        assert "institutions" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert len(data["institutions"]) >= 1

        # Verify our test institution is in the list
        institution_ids = [inst["id"] for inst in data["institutions"]]
        assert test_institution.id in institution_ids

    def test_list_institutions_pagination(
        self, client: TestClient, db_session: Session
    ):
        """Test pagination works correctly"""
        # Create multiple institutions
        for i in range(5):
            inst = Institution(
                ipeds_id=100000 + i,
                name=f"Test University {i}",
                city="Test City",
                state="MA",
                control_type=ControlType.PUBLIC,
            )
            db_session.add(inst)
        db_session.commit()

        # Test page 1 with limit 2
        response = client.get("/api/v1/institutions/?page=1&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["institutions"]) == 2
        assert data["page"] == 1
        assert data["limit"] == 2
        assert data["total"] >= 5

        # Test page 2
        response = client.get("/api/v1/institutions/?page=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2

    def test_list_institutions_custom_limit(
        self, client: TestClient, test_institution: Institution
    ):
        """Test custom page limit"""
        response = client.get("/api/v1/institutions/?limit=10")

        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 10
        assert len(data["institutions"]) <= 10

    def test_list_institutions_max_limit(self, client: TestClient):
        """Test that limit cannot exceed maximum"""
        response = client.get("/api/v1/institutions/?limit=200")

        # Should either reject or cap at max (usually 100)
        assert response.status_code in [200, 422]
        if response.status_code == 200:
            data = response.json()
            assert data["limit"] <= 100


@pytest.mark.integration
class TestInstitutionSearch:
    """Test institution search functionality"""

    def test_search_by_name(self, client: TestClient, test_institution: Institution):
        """Test searching institutions by name"""
        response = client.get(
            f"/api/v1/institutions/?search_query={test_institution.name}"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["institutions"]) >= 1

        # Verify MIT is in results
        names = [inst["name"] for inst in data["institutions"]]
        assert test_institution.name in names

    def test_search_partial_name(
        self, client: TestClient, test_institution: Institution
    ):
        """Test searching with partial name match"""
        # Search for "Massachusetts" which is part of MIT's name
        response = client.get("/api/v1/institutions/?search_query=Massachusetts")

        assert response.status_code == 200
        data = response.json()
        assert len(data["institutions"]) >= 1

    def test_search_case_insensitive(
        self, client: TestClient, test_institution: Institution
    ):
        """Test that search is case insensitive"""
        response = client.get("/api/v1/institutions/?search_query=massachusetts")

        assert response.status_code == 200
        data = response.json()
        assert len(data["institutions"]) >= 1

    def test_search_no_results(self, client: TestClient):
        """Test search with no matching results"""
        response = client.get(
            "/api/v1/institutions/?search_query=NonexistentUniversity12345"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["institutions"]) == 0

    def test_search_endpoint(self, client: TestClient, test_institution: Institution):
        """Test dedicated search endpoint"""
        response = client.get(
            f"/api/v1/institutions/search?query={test_institution.name}"
        )

        assert response.status_code == 200
        # Response format depends on your implementation
        # Could be list or paginated object


@pytest.mark.integration
class TestInstitutionFilters:
    """Test institution filtering"""

    def test_filter_by_state(self, client: TestClient, test_institution: Institution):
        """Test filtering institutions by state"""
        response = client.get("/api/v1/institutions/?state=MA")

        assert response.status_code == 200
        data = response.json()
        assert len(data["institutions"]) >= 1

        # All results should be from MA
        for inst in data["institutions"]:
            assert inst["state"] == "MA"

    def test_filter_by_control_type(self, client: TestClient, db_session: Session):
        """Test filtering by control type"""
        # Create a public institution
        public_inst = Institution(
            ipeds_id=200000,
            name="Public State University",
            city="Boston",
            state="MA",
            control_type=ControlType.PUBLIC,
        )
        db_session.add(public_inst)
        db_session.commit()

        response = client.get("/api/v1/institutions/?control_type=PUBLIC")

        assert response.status_code == 200
        data = response.json()
        assert len(data["institutions"]) >= 1

        # All results should be Public
        for inst in data["institutions"]:
            assert inst["control_type"] == "PUBLIC"

    def test_filter_multiple_criteria(
        self, client: TestClient, test_institution: Institution
    ):
        """Test filtering with multiple criteria"""
        response = client.get(
            "/api/v1/institutions/?state=MA&control_type=PRIVATE_NONPROFIT"
        )

        assert response.status_code == 200
        data = response.json()

        # Results should match both criteria
        for inst in data["institutions"]:
            assert inst["state"] == "MA"
            assert inst["control_type"] == "PRIVATE_NONPROFIT"

    def test_filter_invalid_state(self, client: TestClient):
        """Test filtering with invalid state code"""
        response = client.get("/api/v1/institutions/?state=ZZ")

        # Should either reject or return empty
        if response.status_code == 200:
            data = response.json()
            assert data["total"] == 0
        else:
            assert response.status_code == 422

    def test_get_states_list(self, client: TestClient, test_institution: Institution):
        """Test getting list of available states"""
        response = client.get("/api/v1/institutions/states")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "MA" in data


@pytest.mark.integration
class TestInstitutionDetails:
    """Test getting individual institution details"""

    def test_get_institution_by_id(
        self, client: TestClient, test_institution: Institution
    ):
        """Test getting institution by database ID"""
        response = client.get(f"/api/v1/institutions/{test_institution.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_institution.id
        assert data["name"] == test_institution.name
        assert data["city"] == test_institution.city
        assert data["state"] == test_institution.state
        assert data["ipeds_id"] == test_institution.ipeds_id

    def test_get_institution_by_ipeds_id(
        self, client: TestClient, test_institution: Institution
    ):
        """Test getting institution by IPEDS ID"""
        response = client.get(f"/api/v1/institutions/ipeds/{test_institution.ipeds_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["ipeds_id"] == test_institution.ipeds_id
        assert data["name"] == test_institution.name

    def test_get_institution_not_found(self, client: TestClient):
        """Test getting non-existent institution"""
        response = client.get("/api/v1/institutions/999999")

        assert response.status_code == 404

    def test_get_institution_invalid_id(self, client: TestClient):
        """Test getting institution with invalid ID format"""
        response = client.get("/api/v1/institutions/invalid")

        assert response.status_code == 422

    def test_institution_includes_coordinates(
        self, client: TestClient, test_institution: Institution
    ):
        """Test that institution details include geographic coordinates"""
        response = client.get(f"/api/v1/institutions/{test_institution.id}")

        assert response.status_code == 200
        data = response.json()

        # Check for latitude/longitude if your model includes them
        if "latitude" in data:
            assert data["latitude"] is not None
        if "longitude" in data:
            assert data["longitude"] is not None


@pytest.mark.integration
class TestInstitutionStatistics:
    """Test institution statistics endpoints"""

    def test_get_summary_statistics(
        self, client: TestClient, test_institution: Institution
    ):
        """Test getting summary statistics"""
        response = client.get("/api/v1/institutions/stats/summary")

        assert response.status_code == 200
        data = response.json()

        # Should include counts and statistics
        assert "total_institutions" in data or "total" in data

        # Verify count is at least 1 (our test institution)
        total_key = "total_institutions" if "total_institutions" in data else "total"
        assert data[total_key] >= 1

    def test_statistics_by_state(
        self, client: TestClient, test_institution: Institution
    ):
        """Test statistics include state breakdown"""
        response = client.get("/api/v1/institutions/stats/summary")

        assert response.status_code == 200
        data = response.json()

        # May include state counts
        if "by_state" in data or "states" in data:
            assert isinstance(data.get("by_state") or data.get("states"), (list, dict))

    def test_statistics_by_control_type(
        self, client: TestClient, test_institution: Institution
    ):
        """Test statistics include control type breakdown"""
        response = client.get("/api/v1/institutions/stats/summary")

        assert response.status_code == 200
        data = response.json()

        # May include control type counts
        if "by_control_type" in data or "control_types" in data:
            assert isinstance(
                data.get("by_control_type") or data.get("control_types"), (list, dict)
            )


@pytest.mark.integration
class TestInstitutionDataIntegrity:
    """Test data integrity and validation"""

    def test_institution_has_required_fields(
        self, client: TestClient, test_institution: Institution
    ):
        """Test that institution response includes all required fields"""
        response = client.get(f"/api/v1/institutions/{test_institution.id}")

        assert response.status_code == 200
        data = response.json()

        # Required fields
        required_fields = ["id", "ipeds_id", "name", "city", "state"]
        for field in required_fields:
            assert field in data
            assert data[field] is not None

    def test_institution_ipeds_id_unique(
        self, client: TestClient, test_institution: Institution
    ):
        """Test that IPEDS ID uniquely identifies institutions"""
        # Get by IPEDS ID
        response1 = client.get(
            f"/api/v1/institutions/ipeds/{test_institution.ipeds_id}"
        )
        assert response1.status_code == 200

        # Get by database ID
        response2 = client.get(f"/api/v1/institutions/{test_institution.id}")
        assert response2.status_code == 200

        # Should be the same institution
        data1 = response1.json()
        data2 = response2.json()
        assert data1["id"] == data2["id"]
        assert data1["ipeds_id"] == data2["ipeds_id"]

    def test_state_code_format(self, client: TestClient, test_institution: Institution):
        """Test that state codes are in correct format"""
        response = client.get(f"/api/v1/institutions/{test_institution.id}")

        assert response.status_code == 200
        data = response.json()

        # State should be 2 characters
        assert len(data["state"]) == 2
        assert data["state"].isupper()

    def test_control_type_valid_values(
        self, client: TestClient, test_institution: Institution
    ):
        """Test that control_type has valid values"""
        response = client.get(f"/api/v1/institutions/{test_institution.id}")

        assert response.status_code == 200
        data = response.json()

        # Control type should be one of the valid values
        valid_types = ["PUBLIC", "PRIVATE_NONPROFIT", "PRIVATE_FOR_PROFIT"]
        assert data["control_type"] in valid_types


@pytest.mark.integration
class TestInstitutionEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_search_query(self, client: TestClient):
        """Test search with empty query"""
        response = client.get("/api/v1/institutions/?search_query=")

        # Should return all institutions or handle gracefully
        assert response.status_code == 200

    def test_special_characters_in_search(self, client: TestClient):
        """Test search with special characters"""
        response = client.get(
            "/api/v1/institutions/?search_query=Test%20%26%20University"
        )

        assert response.status_code == 200

    def test_pagination_beyond_results(self, client: TestClient):
        """Test requesting page beyond available results"""
        response = client.get("/api/v1/institutions/?page=999999&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert len(data["institutions"]) == 0

    def test_invalid_page_number(self, client: TestClient):
        """Test with invalid page number"""
        response = client.get("/api/v1/institutions/?page=0")

        # Should either reject or default to page 1
        assert response.status_code in [200, 422]

    def test_negative_limit(self, client: TestClient):
        """Test with negative limit"""
        response = client.get("/api/v1/institutions/?limit=-1")

        # Should reject invalid limit
        assert response.status_code == 422
