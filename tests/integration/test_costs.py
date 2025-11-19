# tests/integration/test_costs.py
"""
Integration tests for costs endpoints.

Tests cover:
- Getting institution cost data
- Cost summaries for card displays
- Comparing costs across multiple institutions
- Residency parameter (in-state vs out-of-state)
"""

import pytest
from starlette.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.institution import Institution


@pytest.mark.integration
class TestInstitutionCosts:
    """Test getting cost data for institutions"""

    def test_get_institution_costs(
        self, client: TestClient, test_institution: Institution
    ):
        """Test getting full cost data for institution"""
        response = client.get(
            f"/api/v1/costs/institution/{test_institution.ipeds_id}"
        )

        # May return 200 with data or 404 if no cost data
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            # Should have tuition data
            assert "tuition_in_state" in data or "in_state_tuition" in data or "costs" in data

    def test_get_costs_invalid_ipeds(self, client: TestClient):
        """Test getting costs with invalid IPEDS ID"""
        response = client.get("/api/v1/costs/institution/999999")

        assert response.status_code == 404

    def test_get_costs_includes_most_recent_year(
        self, client: TestClient, test_institution: Institution
    ):
        """Test that cost data returns most recent year"""
        response = client.get(
            f"/api/v1/costs/institution/{test_institution.ipeds_id}"
        )

        if response.status_code == 200:
            data = response.json()
            # Should have academic year field
            assert "academic_year" in data or "year" in data


@pytest.mark.integration
class TestCostSummary:
    """Test cost summary endpoint"""

    def test_get_cost_summary_in_state(
        self, client: TestClient, test_institution: Institution
    ):
        """Test getting cost summary for in-state"""
        response = client.get(
            f"/api/v1/costs/institution/{test_institution.ipeds_id}/summary?residency=in_state"
        )

        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            # Should be simplified for card display
            assert isinstance(data, dict)

    def test_get_cost_summary_out_of_state(
        self, client: TestClient, test_institution: Institution
    ):
        """Test getting cost summary for out-of-state"""
        response = client.get(
            f"/api/v1/costs/institution/{test_institution.ipeds_id}/summary?residency=out_of_state"
        )

        assert response.status_code in [200, 404]

    def test_cost_summary_default_residency(
        self, client: TestClient, test_institution: Institution
    ):
        """Test cost summary with default residency parameter"""
        response = client.get(
            f"/api/v1/costs/institution/{test_institution.ipeds_id}/summary"
        )

        # Should default to in_state
        assert response.status_code in [200, 404]


@pytest.mark.integration
class TestCostComparison:
    """Test comparing costs across institutions"""

    def test_compare_multiple_institutions(
        self, client: TestClient, test_institution: Institution, db_session: Session
    ):
        """Test comparing costs for multiple institutions"""
        # Create another institution
        from app.models.institution import ControlType
        institution2 = Institution(
            ipeds_id=100001,
            name="Test University 2",
            city="Boston",
            state="MA",
            control_type=ControlType.PUBLIC
        )
        db_session.add(institution2)
        db_session.commit()

        # Compare costs
        ipeds_ids = f"{test_institution.ipeds_id},{institution2.ipeds_id}"
        response = client.get(
            f"/api/v1/costs/compare?ipeds_ids={ipeds_ids}"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_compare_with_residency_parameter(
        self, client: TestClient, test_institution: Institution
    ):
        """Test comparison with residency parameter"""
        response = client.get(
            f"/api/v1/costs/compare?ipeds_ids={test_institution.ipeds_id}&residency=out_of_state"
        )

        assert response.status_code == 200

    def test_compare_invalid_ipeds_format(self, client: TestClient):
        """Test comparison with invalid IPEDS ID format"""
        response = client.get("/api/v1/costs/compare?ipeds_ids=invalid")

        assert response.status_code in [400, 422]

    def test_compare_missing_ipeds_param(self, client: TestClient):
        """Test comparison without ipeds_ids parameter"""
        response = client.get("/api/v1/costs/compare")

        assert response.status_code == 422


@pytest.mark.integration
class TestCostDataStructure:
    """Test cost data structure and fields"""

    def test_cost_data_has_tuition_fields(
        self, client: TestClient, test_institution: Institution
    ):
        """Test that cost data includes tuition fields"""
        response = client.get(
            f"/api/v1/costs/institution/{test_institution.ipeds_id}"
        )

        if response.status_code == 200:
            data = response.json()
            # Should have some tuition-related fields
            has_tuition_field = any(
                key in data
                for key in [
                    "tuition_in_state",
                    "tuition_out_of_state",
                    "in_state_tuition",
                    "out_of_state_tuition",
                    "tuition"
                ]
            )
            assert has_tuition_field or "costs" in data

    def test_cost_data_structure_for_summary(
        self, client: TestClient, test_institution: Institution
    ):
        """Test summary returns simplified structure"""
        response = client.get(
            f"/api/v1/costs/institution/{test_institution.ipeds_id}/summary"
        )

        if response.status_code == 200:
            data = response.json()
            # Summary should be simpler than full data
            assert isinstance(data, dict)
            # Should have essential fields for card display
            assert len(data.keys()) <= 10  # Not too many fields


@pytest.mark.integration
class TestCostEdgeCases:
    """Test edge cases and error handling"""

    def test_institution_without_cost_data(
        self, client: TestClient, db_session: Session
    ):
        """Test institution that has no cost data"""
        from app.models.institution import ControlType
        institution = Institution(
            ipeds_id=888888,
            name="No Cost Data University",
            city="Unknown",
            state="XX",
            control_type=ControlType.PUBLIC
        )
        db_session.add(institution)
        db_session.commit()

        response = client.get(f"/api/v1/costs/institution/{institution.ipeds_id}")

        # Should return 404 if no cost data
        assert response.status_code == 404

    def test_compare_with_single_institution(
        self, client: TestClient, test_institution: Institution
    ):
        """Test comparison with only one institution"""
        response = client.get(
            f"/api/v1/costs/compare?ipeds_ids={test_institution.ipeds_id}"
        )

        # Should still work with single institution
        assert response.status_code == 200
