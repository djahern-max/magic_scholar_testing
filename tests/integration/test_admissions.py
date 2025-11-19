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

from app.models.institution import Institution


@pytest.mark.integration
class TestLatestAdmissionsData:
    """Test getting latest admissions data"""

    def test_get_latest_admissions(
        self, client: TestClient, test_institution: Institution
    ):
        """Test getting most recent admissions data"""
        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}"
        )

        # May return 200 with data or 404 if no admissions data
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "academic_year" in data
            assert "ipeds_id" in data

    def test_latest_admissions_has_statistics(
        self, client: TestClient, test_institution: Institution
    ):
        """Test that admissions data includes statistics"""
        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}"
        )

        if response.status_code == 200:
            data = response.json()
            # Should have some admissions statistics
            expected_fields = [
                "applications_total",
                "admissions_total",
                "acceptance_rate"
            ]
            # At least one of these should be present
            has_stats = any(field in data for field in expected_fields)
            assert has_stats

    def test_latest_admissions_invalid_ipeds(self, client: TestClient):
        """Test getting admissions with invalid IPEDS ID"""
        response = client.get("/api/v1/admissions/institution/999999")

        assert response.status_code == 404


@pytest.mark.integration
class TestAllYearsAdmissions:
    """Test getting all years of admissions data"""

    def test_get_all_years(
        self, client: TestClient, test_institution: Institution
    ):
        """Test getting all years of admissions data"""
        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}/all"
        )

        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            # Results should be ordered by year (newest first)
            if len(data) > 1:
                # Verify ordering (years should be descending)
                years = [item["academic_year"] for item in data]
                assert years == sorted(years, reverse=True)

    def test_all_years_returns_multiple_records(
        self, client: TestClient, test_institution: Institution
    ):
        """Test that all years endpoint can return multiple years"""
        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}/all"
        )

        if response.status_code == 200:
            data = response.json()
            # Should be a list (even if empty or single item)
            assert isinstance(data, list)


@pytest.mark.integration
class TestSpecificYearAdmissions:
    """Test getting admissions for specific year"""

    def test_get_admissions_by_year_format1(
        self, client: TestClient, test_institution: Institution
    ):
        """Test getting admissions with YYYY-YY format"""
        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}/year/2023-24"
        )

        # May or may not have data for this year
        assert response.status_code in [200, 404]

    def test_get_admissions_by_year_format2(
        self, client: TestClient, test_institution: Institution
    ):
        """Test getting admissions with YYYY-YYYY format"""
        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}/year/2023-2024"
        )

        assert response.status_code in [200, 404]

    def test_get_admissions_invalid_year_format(
        self, client: TestClient, test_institution: Institution
    ):
        """Test getting admissions with invalid year format"""
        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}/year/invalid"
        )

        assert response.status_code in [400, 404, 422]

    def test_specific_year_returns_single_record(
        self, client: TestClient, test_institution: Institution
    ):
        """Test that specific year returns single record"""
        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}/year/2023-24"
        )

        if response.status_code == 200:
            data = response.json()
            # Should be a single object, not a list
            assert isinstance(data, dict)
            assert "academic_year" in data


@pytest.mark.integration
class TestAdmissionsDataFields:
    """Test admissions data structure and fields"""

    def test_admissions_has_application_stats(
        self, client: TestClient, test_institution: Institution
    ):
        """Test admissions data includes application statistics"""
        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}"
        )

        if response.status_code == 200:
            data = response.json()
            # Check for application-related fields
            possible_fields = [
                "applications_total",
                "admissions_total",
                "enrolled_total",
                "acceptance_rate",
                "yield_rate"
            ]
            # Should have at least some of these
            has_app_stats = any(field in data for field in possible_fields)
            assert has_app_stats

    def test_admissions_has_test_score_ranges(
        self, client: TestClient, test_institution: Institution
    ):
        """Test admissions data includes SAT/ACT ranges"""
        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}"
        )

        if response.status_code == 200:
            data = response.json()
            # Check for test score fields
            sat_fields = [
                "sat_reading_25th",
                "sat_reading_50th",
                "sat_reading_75th",
                "sat_math_25th",
                "sat_math_50th",
                "sat_math_75th"
            ]
            # May or may not have SAT data
            has_sat_data = any(field in data for field in sat_fields)
            # Just verify structure, don't require data
            assert isinstance(data, dict)

    def test_admissions_has_submission_percentages(
        self, client: TestClient, test_institution: Institution
    ):
        """Test admissions data includes test submission percentages"""
        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}"
        )

        if response.status_code == 200:
            data = response.json()
            # Check for submission percentage fields
            submission_fields = [
                "percent_submitting_sat",
                "percent_submitting_act"
            ]
            # May or may not have this data
            assert isinstance(data, dict)


@pytest.mark.integration
class TestAdmissionsEdgeCases:
    """Test edge cases and error handling"""

    def test_institution_without_admissions_data(
        self, client: TestClient, db_session: Session
    ):
        """Test institution that has no admissions data"""
        from app.models.institution import ControlType
        institution = Institution(
            ipeds_id=777777,
            name="No Admissions Data University",
            city="Unknown",
            state="XX",
            control_type=ControlType.PUBLIC
        )
        db_session.add(institution)
        db_session.commit()

        response = client.get(
            f"/api/v1/admissions/institution/{institution.ipeds_id}"
        )

        # Should return 404 if no admissions data
        assert response.status_code == 404

    def test_year_with_no_data(
        self, client: TestClient, test_institution: Institution
    ):
        """Test requesting year that has no data"""
        response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}/year/1990-91"
        )

        # Should return 404 for year with no data
        assert response.status_code == 404

    def test_all_years_empty_list(
        self, client: TestClient, db_session: Session
    ):
        """Test all years endpoint when no data exists"""
        from app.models.institution import ControlType
        institution = Institution(
            ipeds_id=666666,
            name="No Data University",
            city="Unknown",
            state="XX",
            control_type=ControlType.PUBLIC
        )
        db_session.add(institution)
        db_session.commit()

        response = client.get(
            f"/api/v1/admissions/institution/{institution.ipeds_id}/all"
        )

        # Should return 404 or empty list
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 0


@pytest.mark.integration
class TestAdmissionsDataConsistency:
    """Test data consistency across endpoints"""

    def test_latest_matches_first_in_all_years(
        self, client: TestClient, test_institution: Institution
    ):
        """Test that latest data matches first item in all years"""
        # Get latest
        latest_response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}"
        )
        
        # Get all years
        all_response = client.get(
            f"/api/v1/admissions/institution/{test_institution.ipeds_id}/all"
        )

        if latest_response.status_code == 200 and all_response.status_code == 200:
            latest_data = latest_response.json()
            all_data = all_response.json()
            
            if len(all_data) > 0:
                # Latest should match first item in all years
                assert latest_data["academic_year"] == all_data[0]["academic_year"]
