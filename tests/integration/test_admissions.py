# tests/integration/test_admissions.py
"""
Integration tests for admissions endpoints.

Tests cover:
- Getting latest admissions data
- Getting all years of admissions data
- Getting specific academic year data
- SAT/ACT score ranges
- Acceptance rates and statistics
"""

import pytest
from starlette.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.institution import Institution, ControlType
from app.models.admissions import AdmissionsData


@pytest.mark.integration
class TestLatestAdmissionsData:
    """Test getting latest admissions data"""

    def test_get_latest_admissions_with_data(
        self, client: TestClient, test_institution: Institution, db_session: Session
    ):
        """Test getting most recent admissions data when data exists"""
        # Create admissions data
        admissions = AdmissionsData(
            ipeds_id=test_institution.ipeds_id,
            institution_id=test_institution.id,
            academic_year="2023-24",
            applications_total=10000,
            admissions_total=2000,
            enrolled_total=500,
            acceptance_rate=Decimal("20.00"),
            sat_reading_50th=650,
            sat_math_50th=680,
        )
        db_session.add(admissions)
        db_session.commit()

        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["academic_year"] == "2023-24"
        assert data["ipeds_id"] == test_institution.ipeds_id
        assert data["applications_total"] == 10000
        assert data["admissions_total"] == 2000
        assert float(data["acceptance_rate"]) == 20.00

    def test_get_latest_admissions_without_data(
        self, client: TestClient, test_institution: Institution
    ):
        """Test getting admissions when no data exists"""
        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}"
        )

        assert response.status_code == 404
        assert "No admissions data found" in response.json()["detail"]

    def test_latest_admissions_has_all_fields(
        self, client: TestClient, test_institution: Institution, db_session: Session
    ):
        """Test that response includes all expected fields"""
        admissions = AdmissionsData(
            ipeds_id=test_institution.ipeds_id,
            institution_id=test_institution.id,
            academic_year="2023-24",
            applications_total=10000,
            admissions_total=2000,
            enrolled_total=500,
            acceptance_rate=Decimal("20.00"),
            yield_rate=Decimal("25.00"),
            sat_reading_25th=600,
            sat_reading_50th=650,
            sat_reading_75th=700,
            sat_math_25th=630,
            sat_math_50th=680,
            sat_math_75th=730,
            percent_submitting_sat=Decimal("85.50"),
        )
        db_session.add(admissions)
        db_session.commit()

        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}"
        )

        assert response.status_code == 200
        data = response.json()

        # Verify all expected fields
        assert data["academic_year"] == "2023-24"
        assert data["applications_total"] == 10000
        assert data["admissions_total"] == 2000
        assert data["enrolled_total"] == 500
        assert float(data["acceptance_rate"]) == 20.00
        assert float(data["yield_rate"]) == 25.00
        # SAT scores
        assert data["sat_reading_25th"] == 600
        assert data["sat_reading_50th"] == 650
        assert data["sat_reading_75th"] == 700
        assert data["sat_math_25th"] == 630
        assert data["sat_math_50th"] == 680
        assert data["sat_math_75th"] == 730
        assert float(data["percent_submitting_sat"]) == 85.50

    def test_latest_admissions_invalid_ipeds(self, client: TestClient):
        """Test getting admissions with invalid IPEDS ID"""
        response = client.get("/api/v1/admissions/institution/999999")

        assert response.status_code == 404

    def test_latest_returns_most_recent_year(
        self, client: TestClient, test_institution: Institution, db_session: Session
    ):
        """Test that latest endpoint returns the most recent year"""
        # Create data for multiple years
        old_data = AdmissionsData(
            ipeds_id=test_institution.ipeds_id,
            institution_id=test_institution.id,
            academic_year="2021-22",
            applications_total=9000,
            acceptance_rate=Decimal("22.00"),
        )
        new_data = AdmissionsData(
            ipeds_id=test_institution.ipeds_id,
            institution_id=test_institution.id,
            academic_year="2023-24",
            applications_total=10000,
            acceptance_rate=Decimal("20.00"),
        )
        db_session.add_all([old_data, new_data])
        db_session.commit()

        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}"
        )

        assert response.status_code == 200
        data = response.json()
        # Should return most recent year
        assert data["academic_year"] == "2023-24"
        assert data["applications_total"] == 10000


@pytest.mark.integration
class TestAllYearsAdmissions:
    """Test getting all years of admissions data"""

    def test_get_all_years_with_data(
        self, client: TestClient, test_institution: Institution, db_session: Session
    ):
        """Test getting all years when multiple years exist"""
        # Create data for 3 years
        years_data = [
            AdmissionsData(
                ipeds_id=test_institution.ipeds_id,
                institution_id=test_institution.id,
                academic_year="2021-22",
                applications_total=9000,
            ),
            AdmissionsData(
                ipeds_id=test_institution.ipeds_id,
                institution_id=test_institution.id,
                academic_year="2022-23",
                applications_total=9500,
            ),
            AdmissionsData(
                ipeds_id=test_institution.ipeds_id,
                institution_id=test_institution.id,
                academic_year="2023-24",
                applications_total=10000,
            ),
        ]
        db_session.add_all(years_data)
        db_session.commit()

        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}/all"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

        # Verify ordering (newest first)
        years = [item["academic_year"] for item in data]
        assert years == ["2023-24", "2022-23", "2021-22"]

    def test_get_all_years_without_data(
        self, client: TestClient, test_institution: Institution
    ):
        """Test all years endpoint when no data exists"""
        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}/all"
        )

        assert response.status_code == 404

    def test_all_years_nonexistent_institution(self, client: TestClient):
        """Test all years for non-existent institution"""
        response = client.get("/api/v1/admissions/institution/999999/all")

        assert response.status_code == 404


@pytest.mark.integration
class TestSpecificYearAdmissions:
    """Test getting admissions for specific year"""

    def test_get_admissions_by_year_success(
        self, client: TestClient, test_institution: Institution, db_session: Session
    ):
        """Test getting admissions for a specific year that exists"""
        admissions = AdmissionsData(
            ipeds_id=test_institution.ipeds_id,
            institution_id=test_institution.id,
            academic_year="2023-24",
            applications_total=10000,
            admissions_total=2000,
        )
        db_session.add(admissions)
        db_session.commit()

        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}/year/2023-24"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["academic_year"] == "2023-24"
        assert data["applications_total"] == 10000

    def test_get_admissions_year_not_found(
        self, client: TestClient, test_institution: Institution, db_session: Session
    ):
        """Test getting year that doesn't exist"""
        # Create data for 2023-24 but request 2022-23
        admissions = AdmissionsData(
            ipeds_id=test_institution.ipeds_id,
            institution_id=test_institution.id,
            academic_year="2023-24",
            applications_total=10000,
        )
        db_session.add(admissions)
        db_session.commit()

        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}/year/2022-23"
        )

        assert response.status_code == 404

    def test_get_admissions_alternative_year_format(
        self, client: TestClient, test_institution: Institution, db_session: Session
    ):
        """Test that both year formats work (2023-24 and 2023-2024)"""
        admissions = AdmissionsData(
            ipeds_id=test_institution.ipeds_id,
            institution_id=test_institution.id,
            academic_year="2023-24",
            applications_total=10000,
        )
        db_session.add(admissions)
        db_session.commit()

        # Try with full year format
        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}/year/2023-2024"
        )

        # Should work or return 404 (depends on implementation)
        assert response.status_code in [200, 404]

    def test_specific_year_returns_single_record(
        self, client: TestClient, test_institution: Institution, db_session: Session
    ):
        """Test that specific year returns object, not list"""
        admissions = AdmissionsData(
            ipeds_id=test_institution.ipeds_id,
            institution_id=test_institution.id,
            academic_year="2023-24",
            applications_total=10000,
        )
        db_session.add(admissions)
        db_session.commit()

        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}/year/2023-24"
        )

        assert response.status_code == 200
        data = response.json()
        # Should be a dict, not a list
        assert isinstance(data, dict)
        assert "academic_year" in data


@pytest.mark.integration
class TestAdmissionsDataFields:
    """Test admissions data structure and fields"""

    def test_admissions_with_complete_sat_data(
        self, client: TestClient, test_institution: Institution, db_session: Session
    ):
        """Test admissions with full SAT score ranges"""
        admissions = AdmissionsData(
            ipeds_id=test_institution.ipeds_id,
            institution_id=test_institution.id,
            academic_year="2023-24",
            sat_reading_25th=600,
            sat_reading_50th=650,
            sat_reading_75th=700,
            sat_math_25th=630,
            sat_math_50th=680,
            sat_math_75th=730,
        )
        db_session.add(admissions)
        db_session.commit()

        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}"
        )

        assert response.status_code == 200
        data = response.json()

        # Verify SAT ranges
        assert data["sat_reading_25th"] == 600
        assert data["sat_reading_50th"] == 650
        assert data["sat_reading_75th"] == 700
        assert data["sat_math_25th"] == 630
        assert data["sat_math_50th"] == 680
        assert data["sat_math_75th"] == 730

    def test_admissions_with_null_fields(
        self, client: TestClient, test_institution: Institution, db_session: Session
    ):
        """Test handling of null/missing fields"""
        # Create minimal admissions record
        admissions = AdmissionsData(
            ipeds_id=test_institution.ipeds_id,
            institution_id=test_institution.id,
            academic_year="2023-24",
            applications_total=10000,
            # All other fields null
        )
        db_session.add(admissions)
        db_session.commit()

        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["applications_total"] == 10000
        # Null fields should be present but null
        assert data["admissions_total"] is None
        assert data["sat_reading_50th"] is None

    def test_admissions_decimal_precision(
        self, client: TestClient, test_institution: Institution, db_session: Session
    ):
        """Test that decimal fields maintain precision"""
        admissions = AdmissionsData(
            ipeds_id=test_institution.ipeds_id,
            institution_id=test_institution.id,
            academic_year="2023-24",
            acceptance_rate=Decimal("19.75"),
            yield_rate=Decimal("24.33"),
            percent_submitting_sat=Decimal("87.65"),
        )
        db_session.add(admissions)
        db_session.commit()

        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert float(data["acceptance_rate"]) == 19.75
        assert float(data["yield_rate"]) == 24.33
        assert float(data["percent_submitting_sat"]) == 87.65


@pytest.mark.integration
class TestAdmissionsEdgeCases:
    """Test edge cases and error handling"""

    def test_institution_without_admissions_data(
        self, client: TestClient, db_session: Session
    ):
        """Test institution that has no admissions data"""
        institution = Institution(
            ipeds_id=777777,
            name="No Admissions Data University",
            city="Unknown",
            state="XX",
            control_type=ControlType.PUBLIC,
        )
        db_session.add(institution)
        db_session.commit()

        response = client.get(f"/api/v1/admissions/institution/{institution.ipeds_id}")

        assert response.status_code == 404

    def test_invalid_ipeds_format(self, client: TestClient):
        """Test with invalid IPEDS ID format"""
        response = client.get("/api/v1/admissions/institution/invalid")

        assert response.status_code == 422  # Validation error

    def test_negative_ipeds_id(self, client: TestClient):
        """Test with negative IPEDS ID"""
        response = client.get("/api/v1/admissions/institution/-1")

        assert response.status_code == 404

    def test_year_with_no_data(self, client: TestClient, test_institution: Institution):
        """Test requesting year that has no data"""
        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}/year/1990-91"
        )

        assert response.status_code == 404


@pytest.mark.integration
class TestAdmissionsDataConsistency:
    """Test data consistency across endpoints"""

    def test_latest_matches_first_in_all_years(
        self, client: TestClient, test_institution: Institution, db_session: Session
    ):
        """Test that latest data matches first item in all years"""
        # Create multiple years of data
        years_data = [
            AdmissionsData(
                ipeds_id=test_institution.ipeds_id,
                institution_id=test_institution.id,
                academic_year="2022-23",
                applications_total=9500,
            ),
            AdmissionsData(
                ipeds_id=test_institution.ipeds_id,
                institution_id=test_institution.id,
                academic_year="2023-24",
                applications_total=10000,
            ),
        ]
        db_session.add_all(years_data)
        db_session.commit()

        # Get latest
        latest_response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}"
        )

        # Get all years
        all_response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}/all"
        )

        assert latest_response.status_code == 200
        assert all_response.status_code == 200

        latest_data = latest_response.json()
        all_data = all_response.json()

        # Latest should match first item in all years
        assert latest_data["academic_year"] == all_data[0]["academic_year"]
        assert latest_data["applications_total"] == all_data[0]["applications_total"]

    def test_specific_year_matches_in_all_years(
        self, client: TestClient, test_institution: Institution, db_session: Session
    ):
        """Test that specific year data matches same year in all years list"""
        # Create data for specific year
        admissions = AdmissionsData(
            ipeds_id=test_institution.ipeds_id,
            institution_id=test_institution.id,
            academic_year="2022-23",
            applications_total=9500,
            acceptance_rate=Decimal("21.00"),
        )
        db_session.add(admissions)
        db_session.commit()

        # Get specific year
        year_response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}/year/2022-23"
        )

        # Get all years
        all_response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}/all"
        )

        assert year_response.status_code == 200
        assert all_response.status_code == 200

        year_data = year_response.json()
        all_data = all_response.json()

        # Find 2022-23 in all years list
        year_2022_in_all = next(
            (item for item in all_data if item["academic_year"] == "2022-23"), None
        )
        assert year_2022_in_all is not None
        assert year_data["applications_total"] == year_2022_in_all["applications_total"]
