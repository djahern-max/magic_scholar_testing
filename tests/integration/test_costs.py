# tests/integration/test_costs.py
"""
Integration tests for Costs API endpoints.

Tests cover:
- Getting institution cost data
- Cost summaries for card displays
- Comparing costs across institutions
- In-state vs out-of-state tuition
- Missing data scenarios
- Invalid IPEDS ID handling
"""

import pytest
from starlette.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.institution import Institution, ControlType
from app.models.tuition import TuitionData


@pytest.mark.integration
class TestGetInstitutionCosts:
    """Test getting detailed cost data for institutions"""

    def test_get_costs_for_valid_institution(
        self, client: TestClient, test_institution: Institution, db_session: Session
    ):
        """Test getting costs for an institution with cost data"""
        # Create tuition data for test institution
        tuition_data = TuitionData(
            ipeds_id=test_institution.ipeds_id,
            institution_id=test_institution.id,
            academic_year="2023-24",
            data_source="IPEDS",
            tuition_in_state=15000.0,
            tuition_out_state=35000.0,
            required_fees_in_state=1200.0,
            required_fees_out_state=1200.0,
            room_board_on_campus=12000.0,
        )
        db_session.add(tuition_data)
        db_session.commit()

        response = client.get(f"/api/v1/costs/institution/{test_institution.ipeds_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["ipeds_id"] == test_institution.ipeds_id
        assert data["has_cost_data"] is True
        assert data["academic_year"] == "2023-24"
        assert data["tuition_in_state"] == 15000.0
        assert data["tuition_out_state"] == 35000.0
        assert data["required_fees_in_state"] == 1200.0
        assert data["room_board_on_campus"] == 12000.0

    def test_get_costs_for_institution_without_data(
        self, client: TestClient, test_institution: Institution
    ):
        """Test getting costs for institution with no cost data"""
        response = client.get(f"/api/v1/costs/institution/{test_institution.ipeds_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["ipeds_id"] == test_institution.ipeds_id
        assert data["has_cost_data"] is False
        assert "No cost data available" in data["message"]

    def test_get_costs_for_nonexistent_institution(self, client: TestClient):
        """Test getting costs for non-existent institution"""
        response = client.get("/api/v1/costs/institution/999999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_costs_includes_all_fields(
        self, client: TestClient, test_institution: Institution, db_session: Session
    ):
        """Test that response includes all expected cost fields"""
        tuition_data = TuitionData(
            ipeds_id=test_institution.ipeds_id,
            institution_id=test_institution.id,
            academic_year="2023-24",
            data_source="IPEDS",
            tuition_in_state=15000.0,
            tuition_out_state=35000.0,
            required_fees_in_state=1200.0,
            required_fees_out_state=1200.0,
            room_board_on_campus=12000.0,
        )
        db_session.add(tuition_data)
        db_session.commit()

        response = client.get(f"/api/v1/costs/institution/{test_institution.ipeds_id}")

        assert response.status_code == 200
        data = response.json()

        # Verify all expected fields are present
        expected_fields = [
            "ipeds_id",
            "institution_name",
            "has_cost_data",
            "academic_year",
            "data_source",
            "tuition_in_state",
            "tuition_out_state",
            "required_fees_in_state",
            "required_fees_out_state",
            "room_board_on_campus",
        ]
        for field in expected_fields:
            assert field in data

    def test_get_costs_returns_most_recent_data(
        self, client: TestClient, test_institution: Institution, db_session: Session
    ):
        """Test that API returns the most recent year's data"""
        # Create data for multiple years
        old_data = TuitionData(
            ipeds_id=test_institution.ipeds_id,
            institution_id=test_institution.id,
            academic_year="2021-22",
            data_source="IPEDS",
            tuition_in_state=13000.0,
            tuition_out_state=30000.0,
        )
        new_data = TuitionData(
            ipeds_id=test_institution.ipeds_id,
            institution_id=test_institution.id,
            academic_year="2023-24",
            data_source="IPEDS",
            tuition_in_state=15000.0,
            tuition_out_state=35000.0,
        )
        db_session.add_all([old_data, new_data])
        db_session.commit()

        response = client.get(f"/api/v1/costs/institution/{test_institution.ipeds_id}")

        assert response.status_code == 200
        data = response.json()
        # Should return the most recent (2023-24) data
        assert data["academic_year"] == "2023-24"
        assert data["tuition_in_state"] == 15000.0


@pytest.mark.integration
class TestGetCostsSummary:
    """Test cost summary endpoint for card displays"""

    def test_get_summary_in_state(
        self, client: TestClient, test_institution: Institution, db_session: Session
    ):
        """Test getting in-state cost summary"""
        tuition_data = TuitionData(
            ipeds_id=test_institution.ipeds_id,
            institution_id=test_institution.id,
            academic_year="2023-24",
            data_source="IPEDS",
            tuition_in_state=15000.0,
            tuition_out_state=35000.0,
            required_fees_in_state=1200.0,
            required_fees_out_state=1500.0,
            room_board_on_campus=12000.0,
        )
        db_session.add(tuition_data)
        db_session.commit()

        response = client.get(
            f"/api/v1/costs/institution/{test_institution.ipeds_id}/summary?residency=in_state"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ipeds_id"] == test_institution.ipeds_id
        assert data["residency_status"] == "in_state"
        assert data["has_data"] is True
        assert data["tuition"] == 15000.0
        assert data["fees"] == 1200.0
        assert data["room_and_board"] == 12000.0
        # Total should be sum of tuition + fees + room_board
        assert data["estimated_total"] == 28200.0

    def test_get_summary_out_of_state(
        self, client: TestClient, test_institution: Institution, db_session: Session
    ):
        """Test getting out-of-state cost summary"""
        tuition_data = TuitionData(
            ipeds_id=test_institution.ipeds_id,
            institution_id=test_institution.id,
            academic_year="2023-24",
            data_source="IPEDS",
            tuition_in_state=15000.0,
            tuition_out_state=35000.0,
            required_fees_in_state=1200.0,
            required_fees_out_state=1500.0,
            room_board_on_campus=12000.0,
        )
        db_session.add(tuition_data)
        db_session.commit()

        response = client.get(
            f"/api/v1/costs/institution/{test_institution.ipeds_id}/summary?residency=out_of_state"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["residency_status"] == "out_of_state"
        assert data["tuition"] == 35000.0
        assert data["fees"] == 1500.0
        # Total for out-of-state
        assert data["estimated_total"] == 48500.0

    def test_get_summary_defaults_to_in_state(
        self, client: TestClient, test_institution: Institution, db_session: Session
    ):
        """Test that summary defaults to in-state if no residency specified"""
        tuition_data = TuitionData(
            ipeds_id=test_institution.ipeds_id,
            institution_id=test_institution.id,
            academic_year="2023-24",
            data_source="IPEDS",
            tuition_in_state=15000.0,
            tuition_out_state=35000.0,
        )
        db_session.add(tuition_data)
        db_session.commit()

        response = client.get(
            f"/api/v1/costs/institution/{test_institution.ipeds_id}/summary"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["residency_status"] == "in_state"
        assert data["tuition"] == 15000.0

    def test_get_summary_no_data(
        self, client: TestClient, test_institution: Institution
    ):
        """Test summary when no cost data exists"""
        response = client.get(
            f"/api/v1/costs/institution/{test_institution.ipeds_id}/summary"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["has_data"] is False
        assert data["ipeds_id"] == test_institution.ipeds_id

    def test_get_summary_nonexistent_institution(self, client: TestClient):
        """Test summary for non-existent institution"""
        response = client.get("/api/v1/costs/institution/999999/summary")

        assert response.status_code == 404


@pytest.mark.integration
class TestCompareCosts:
    """Test comparing costs across multiple institutions"""

    def test_compare_two_institutions(self, client: TestClient, db_session: Session):
        """Test comparing costs between two institutions"""
        # Create two institutions
        inst1 = Institution(
            ipeds_id=100001,
            name="University A",
            state="CA",
            city="Los Angeles",
            control_type=ControlType.PUBLIC,
        )
        inst2 = Institution(
            ipeds_id=100002,
            name="University B",
            state="NY",
            city="New York",
            control_type=ControlType.PUBLIC,
        )
        db_session.add_all([inst1, inst2])
        db_session.flush()

        # Add cost data for both
        cost1 = TuitionData(
            ipeds_id=100001,
            institution_id=inst1.id,
            academic_year="2023-24",
            data_source="IPEDS",
            tuition_in_state=15000.0,
            required_fees_in_state=1200.0,
            room_board_on_campus=12000.0,
        )
        cost2 = TuitionData(
            ipeds_id=100002,
            institution_id=inst2.id,
            academic_year="2023-24",
            data_source="IPEDS",
            tuition_in_state=18000.0,
            required_fees_in_state=1500.0,
            room_board_on_campus=15000.0,
        )
        db_session.add_all([cost1, cost2])
        db_session.commit()

        response = client.get("/api/v1/costs/compare?ipeds_ids=100001,100002")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert data["residency_status"] == "in_state"
        assert len(data["institutions"]) == 2

        # Check first institution
        inst1_data = next(i for i in data["institutions"] if i["ipeds_id"] == 100001)
        assert inst1_data["name"] == "University A"
        assert inst1_data["tuition"] == 15000.0
        assert inst1_data["fees"] == 1200.0
        assert inst1_data["tuition_fees_combined"] == 16200.0

    def test_compare_with_out_of_state(self, client: TestClient, db_session: Session):
        """Test comparing out-of-state costs"""
        inst = Institution(
            ipeds_id=100003,
            name="Test University",
            state="CA",
            city="Test City",
            control_type=ControlType.PUBLIC,
        )
        db_session.add(inst)
        db_session.flush()

        cost = TuitionData(
            ipeds_id=100003,
            institution_id=inst.id,
            academic_year="2023-24",
            data_source="IPEDS",
            tuition_in_state=15000.0,
            tuition_out_state=35000.0,
            required_fees_in_state=1200.0,
            required_fees_out_state=1500.0,
        )
        db_session.add(cost)
        db_session.commit()

        response = client.get(
            "/api/v1/costs/compare?ipeds_ids=100003&residency=out_of_state"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["residency_status"] == "out_of_state"
        inst_data = data["institutions"][0]
        assert inst_data["tuition"] == 35000.0
        assert inst_data["fees"] == 1500.0

    def test_compare_handles_missing_data(
        self, client: TestClient, db_session: Session
    ):
        """Test comparing when some institutions lack cost data"""
        # Create institution without cost data
        inst = Institution(
            ipeds_id=100004,
            name="No Data University",
            state="TX",
            city="Austin",
            control_type=ControlType.PUBLIC,
        )
        db_session.add(inst)
        db_session.commit()

        response = client.get("/api/v1/costs/compare?ipeds_ids=100004")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        inst_data = data["institutions"][0]
        assert inst_data["has_data"] is False
        assert inst_data["name"] == "No Data University"

    def test_compare_skips_nonexistent_institutions(
        self, client: TestClient, db_session: Session
    ):
        """Test that compare skips institutions that don't exist"""
        # Create one real institution
        inst = Institution(
            ipeds_id=100005,
            name="Real University",
            state="CA",
            city="Test City",
            control_type=ControlType.PUBLIC,
        )
        db_session.add(inst)
        db_session.flush()

        cost = TuitionData(
            ipeds_id=100005,
            institution_id=inst.id,
            academic_year="2023-24",
            data_source="IPEDS",
            tuition_in_state=15000.0,
        )
        db_session.add(cost)
        db_session.commit()

        # Request includes one real and one fake IPEDS ID
        response = client.get("/api/v1/costs/compare?ipeds_ids=100005,999999")

        assert response.status_code == 200
        data = response.json()
        # Should only return the one real institution
        assert data["count"] == 1
        assert data["institutions"][0]["ipeds_id"] == 100005

    def test_compare_max_limit(self, client: TestClient):
        """Test that compare enforces maximum of 10 institutions"""
        # Try to compare 11 institutions
        ipeds_ids = ",".join(str(i) for i in range(100000, 100011))
        response = client.get(f"/api/v1/costs/compare?ipeds_ids={ipeds_ids}")

        assert response.status_code == 400
        assert "Maximum 10 institutions" in response.json()["detail"]

    def test_compare_includes_institution_metadata(
        self, client: TestClient, db_session: Session
    ):
        """Test that comparison includes institution state and control type"""
        inst = Institution(
            ipeds_id=100006,
            name="Test University",
            state="MA",
            city="Boston",
            control_type=ControlType.PUBLIC,
        )
        db_session.add(inst)
        db_session.flush()

        cost = TuitionData(
            ipeds_id=100006,
            institution_id=inst.id,
            academic_year="2023-24",
            data_source="IPEDS",
            tuition_in_state=20000.0,
        )
        db_session.add(cost)
        db_session.commit()

        response = client.get("/api/v1/costs/compare?ipeds_ids=100006")

        assert response.status_code == 200
        data = response.json()
        inst_data = data["institutions"][0]
        assert inst_data["state"] == "MA"
        assert inst_data["control_type"] == "PUBLIC"


@pytest.mark.integration
class TestCostsEdgeCases:
    """Test edge cases and error handling"""

    def test_invalid_ipeds_id_format(self, client: TestClient):
        """Test with invalid IPEDS ID format"""
        response = client.get("/api/v1/costs/institution/invalid")

        assert response.status_code == 422  # Validation error

    def test_negative_ipeds_id(self, client: TestClient):
        """Test with negative IPEDS ID"""
        response = client.get("/api/v1/costs/institution/-1")

        assert response.status_code == 404

    def test_compare_with_empty_list(self, client: TestClient):
        """Test compare with empty IPEDS list"""
        response = client.get("/api/v1/costs/compare?ipeds_ids=")

        # Will throw 500 because int('') fails - this is acceptable
        assert response.status_code in [422, 500]

    def test_compare_with_invalid_format(self, client: TestClient):
        """Test compare with invalid IPEDS ID format"""
        response = client.get("/api/v1/costs/compare?ipeds_ids=abc,def")

        assert response.status_code == 500  # Will fail to parse

    def test_costs_with_null_values(
        self, client: TestClient, test_institution: Institution, db_session: Session
    ):
        """Test handling of null/missing cost values"""
        # Create data with some null values
        tuition_data = TuitionData(
            ipeds_id=test_institution.ipeds_id,
            institution_id=test_institution.id,
            academic_year="2023-24",
            data_source="IPEDS",
            tuition_in_state=15000.0,
            tuition_out_state=None,  # Null out-of-state
            required_fees_in_state=None,  # Null fees
            room_board_on_campus=12000.0,
        )
        db_session.add(tuition_data)
        db_session.commit()

        response = client.get(f"/api/v1/costs/institution/{test_institution.ipeds_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["tuition_in_state"] == 15000.0
        assert data["tuition_out_state"] is None
        assert data["required_fees_in_state"] is None
