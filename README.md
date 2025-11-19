# MagicScholar Testing Suite

A comprehensive testing repository for the MagicScholar backend API, focused on integration and unit testing of all endpoints except OAuth providers.

## Overview

This repository contains automated tests for MagicScholar's FastAPI backend, ensuring reliability and correctness across authentication, institutions, scholarships, profiles, costs, admissions, and application tracking features.

## Project Structure

```
magic_scholar_testing/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures and configuration
│   ├── integration/             # Integration tests
│   │   ├── __init__.py
│   │   ├── test_auth_flow.py           ✅ COMPLETE (24 tests)
│   │   ├── test_institutions.py        ✅ COMPLETE (31 tests)
│   │   ├── test_scholarships.py        🚧 TODO
│   │   ├── test_profiles.py            🚧 TODO
│   │   ├── test_costs.py               🚧 TODO
│   │   ├── test_admissions.py          🚧 TODO
│   │   ├── test_scholarship_tracking.py 🚧 TODO
│   │   └── test_college_tracking.py    🚧 TODO
│   ├── unit/                    # Unit tests
│   │   └── __init__.py
│   └── docs/                    # Test documentation
└── README.md
```

## Testing Progress

### ✅ Completed Endpoints (55 tests)

#### Authentication (`test_auth_flow.py`) - 24 tests
- ✅ User registration (7 tests)
- ✅ User login (OAuth2 form & JSON) (6 tests)
- ✅ Protected endpoints & JWT validation (6 tests)
- ✅ Logout functionality (2 tests)
- ✅ Multiple users & admin scenarios (3 tests)

#### Institutions (`test_institutions.py`) - 31 tests
- ✅ Listing & pagination (4 tests)
- ✅ Search functionality (5 tests)
- ✅ Filtering (state, control type) (5 tests)
- ✅ Institution details (5 tests)
- ✅ Statistics & summaries (3 tests)
- ✅ Data integrity (4 tests)
- ✅ Edge cases (5 tests)

### 🚧 Pending Endpoints (Need Testing)

#### 1. Scholarships API (`/api/v1/scholarships/`)
**Priority: HIGH**
- [ ] `POST /api/v1/scholarships/` - Create scholarship (Admin)
- [ ] `GET /api/v1/scholarships/` - Search/filter scholarships
- [ ] `GET /api/v1/scholarships/{scholarship_id}` - Get single scholarship
- [ ] `PATCH /api/v1/scholarships/{scholarship_id}` - Update scholarship (Admin)
- [ ] `DELETE /api/v1/scholarships/{scholarship_id}` - Delete scholarship (Admin)
- [ ] `GET /api/v1/scholarships/list` - Simple list
- [ ] `GET /api/v1/scholarships/upcoming-deadlines` - Upcoming deadlines
- [ ] `POST /api/v1/scholarships/bulk` - Bulk create (Admin)

**Test Coverage Needed:**
- CRUD operations with admin authentication
- Complex filtering (type, GPA, amount, deadline, academic year)
- Sorting (created_at, amount, deadline, views)
- Verification & featured flags
- Pagination and search
- Authorization (admin-only operations)
- Data validation

#### 2. Profiles API (`/api/v1/profiles/me/`)
**Priority: HIGH**
- [ ] `GET /api/v1/profiles/me` - Get current user profile
- [ ] `PUT /api/v1/profiles/me` - Update profile
- [ ] `GET /api/v1/profiles/me/matching-institutions` - Get matching institutions
- [ ] `GET /api/v1/profiles/me/settings` - Get user settings
- [ ] `PATCH /api/v1/profiles/me/settings` - Update settings (confetti_enabled)
- [ ] `POST /api/v1/profiles/me/upload-headshot` - Upload profile image
- [ ] `POST /api/v1/profiles/me/upload-resume-and-update` - Upload resume & parse

**Test Coverage Needed:**
- Profile CRUD operations
- File uploads (headshot, resume)
- Resume parsing integration
- Matching algorithm
- Settings management
- Profile data validation (GPA, test scores, graduation year)
- Array fields (extracurriculars, work_experience, honors, skills)

#### 3. Costs API (`/api/v1/costs/`)
**Priority: MEDIUM**
- [ ] `GET /api/v1/costs/institution/{ipeds_id}` - Get institution costs
- [ ] `GET /api/v1/costs/institution/{ipeds_id}/summary` - Cost summary
- [ ] `GET /api/v1/costs/compare` - Compare costs across institutions

**Test Coverage Needed:**
- Cost data retrieval
- In-state vs out-of-state tuition
- Cost summaries for card displays
- Multi-institution comparisons
- Invalid IPEDS ID handling
- Missing cost data scenarios

#### 4. Admissions API (`/api/v1/admissions/`)
**Priority: MEDIUM**
- [ ] `GET /api/v1/admissions/institution/{ipeds_id}` - Latest admissions data
- [ ] `GET /api/v1/admissions/institution/{ipeds_id}/all` - All years
- [ ] `GET /api/v1/admissions/institution/{ipeds_id}/year/{academic_year}` - Specific year

**Test Coverage Needed:**
- Admissions data retrieval (latest & all years)
- Academic year filtering
- SAT/ACT score ranges
- Acceptance rate calculations
- Test submission percentages
- Historical trends
- Data validation

#### 5. Scholarship Tracking (`/api/v1/scholarship-tracking/`)
**Priority: HIGH**
- [ ] `GET /api/v1/scholarship-tracking/dashboard` - Dashboard with stats
- [ ] `POST /api/v1/scholarship-tracking/applications` - Save/bookmark scholarship
- [ ] `GET /api/v1/scholarship-tracking/applications` - Get applications (filtered/sorted)
- [ ] `GET /api/v1/scholarship-tracking/applications/{application_id}` - Get single
- [ ] `PUT /api/v1/scholarship-tracking/applications/{application_id}` - Update application
- [ ] `DELETE /api/v1/scholarship-tracking/applications/{application_id}` - Remove tracking
- [ ] `POST /api/v1/scholarship-tracking/applications/{application_id}/mark-submitted`
- [ ] `POST /api/v1/scholarship-tracking/applications/{application_id}/mark-accepted`
- [ ] `POST /api/v1/scholarship-tracking/applications/{application_id}/mark-rejected`

**Test Coverage Needed:**
- Dashboard statistics (total apps, status counts, potential value)
- Application status transitions
- Automatic timestamp handling (started_at, submitted_at, decision_date)
- Filtering & sorting
- Upcoming deadlines calculation
- Overdue detection
- User data isolation
- Award amount tracking

#### 6. College Tracking (`/api/v1/college-tracking/`)
**Priority: HIGH**
- [ ] `GET /api/v1/college-tracking/dashboard` - Dashboard with stats
- [ ] `POST /api/v1/college-tracking/applications` - Save/bookmark college
- [ ] `GET /api/v1/college-tracking/applications` - Get applications (filtered/sorted)
- [ ] `GET /api/v1/college-tracking/applications/{application_id}` - Get single
- [ ] `PUT /api/v1/college-tracking/applications/{application_id}` - Update application
- [ ] `DELETE /api/v1/college-tracking/applications/{application_id}` - Remove tracking
- [ ] `POST /api/v1/college-tracking/applications/{application_id}/mark-submitted`
- [ ] `POST /api/v1/college-tracking/applications/{application_id}/mark-accepted`
- [ ] `POST /api/v1/college-tracking/applications/{application_id}/mark-rejected`
- [ ] `POST /api/v1/college-tracking/applications/{application_id}/mark-waitlisted`

**Test Coverage Needed:**
- Dashboard statistics (total apps, status counts)
- Application types (early decision, early action, regular, rolling)
- Status transitions (researching → planning → in_progress → submitted → accepted/waitlisted/rejected/declined/enrolled)
- Automatic timestamp handling
- Decision date tracking
- Fee waiver management
- Portal information storage
- Filtering & sorting

#### 7. Health & System Routes
**Priority: LOW**
- [ ] `GET /` - Root endpoint
- [ ] `GET /health` - Health check
- [ ] `GET /routes-simple` - Route listing

### ⏭️ Explicitly Excluded

#### OAuth Endpoints (Testing locally without OAuth setup)
- `GET /api/v1/oauth/google/url`
- `GET /api/v1/oauth/google/callback`
- `GET /api/v1/oauth/linkedin/url`
- `GET /api/v1/oauth/linkedin/callback`
- `DELETE /api/v1/oauth/cleanup-expired-states`

## Technology Stack

- **Backend Framework:** FastAPI (Python)
- **Database:** PostgreSQL (local testing)
- **Testing Framework:** pytest
- **Test Client:** Starlette TestClient
- **ORM:** SQLAlchemy (sync mode)
- **Authentication:** JWT (jose)

## Setup Instructions

### Prerequisites
```bash
# Python 3.11+
python --version

# PostgreSQL running locally
psql --version

# MagicScholar backend running
# (Assumed at localhost:8000)
```

### Installation

1. **Clone and navigate:**
```bash
cd /Users/ryze.ai/projects/magic_scholar_testing
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install pytest pytest-asyncio starlette sqlalchemy psycopg2-binary \
            python-jose[cryptography] passlib[bcrypt] python-multipart \
            pydantic[email] faker pytest-cov pytest-xdist pytest-timeout
```

4. **Configure test database:**
```bash
# Create test database
createdb magicscholar_test

# Set environment variable (or use .env file)
export DATABASE_URL="postgresql://postgres:@localhost:5432/magicscholar_test"
```

5. **Ensure backend is accessible:**
```bash
# Backend should be running at localhost:8000
curl http://localhost:8000/health
```

## Running Tests

### Run all tests
```bash
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/integration/test_auth_flow.py -v
pytest tests/integration/test_institutions.py -v
pytest tests/integration/test_scholarships.py -v
pytest tests/integration/.py -v
```

### Run with coverage
```bash
pytest tests/ --cov=tests --cov-report=html
```

### Run with parallel execution
```bash
pytest tests/ -n auto
```

### Run specific test class or method
```bash
pytest tests/integration/test_auth_flow.py::TestUserRegistration -v
pytest tests/integration/test_auth_flow.py::TestUserRegistration::test_register_new_user_success -v
```

## Test Results So Far

**Total Tests Passing: 55/55 (100%)**

```
Authentication:     24/24 ✅ (100%)
Institutions:       31/31 ✅ (100%)
Scholarships:        0    🚧 (Pending)
Profiles:            0    🚧 (Pending)
Costs:               0    🚧 (Pending)
Admissions:          0    🚧 (Pending)
Scholarship Track:   0    🚧 (Pending)
College Track:       0    🚧 (Pending)
```

## Test Structure

### Fixtures (conftest.py)
- `db_session` - Clean database session per test
- `client` - TestClient instance
- `test_user` / `test_user_2` - Regular users
- `admin_user` - Admin user
- `user_token` / `admin_token` - JWT tokens
- `auth_headers` / `admin_headers` - Authorization headers
- `test_profile` - Sample user profile
- `test_institution` - Sample institution (MIT)
- `test_scholarship` - Sample scholarship

### Test Organization
Each test file follows this pattern:
```python
@pytest.mark.integration
class TestFeatureGroup:
    """Test specific feature area"""
    
    def test_happy_path(self, client, fixtures):
        """Test successful operation"""
        
    def test_validation(self, client):
        """Test input validation"""
        
    def test_authorization(self, client, auth_headers):
        """Test authorization requirements"""
        
    def test_edge_cases(self, client):
        """Test edge cases and error handling"""
```

## Development Workflow

### Adding New Tests

1. **Create test file:**
```bash
touch tests/integration/test_scholarships.py
```

2. **Import necessary modules:**
```python
import pytest
from starlette.testclient import TestClient
from sqlalchemy.orm import Session
```

3. **Organize into test classes:**
```python
@pytest.mark.integration
class TestScholarshipCreation:
    """Test scholarship creation"""
    
@pytest.mark.integration  
class TestScholarshipSearch:
    """Test scholarship search and filtering"""
```

4. **Use existing fixtures:**
```python
def test_create_scholarship(
    self,
    client: TestClient,
    admin_headers: dict
):
    response = client.post(
        "/api/v1/scholarships/",
        json=scholarship_data,
        headers=admin_headers
    )
    assert response.status_code == 201
```

5. **Run tests:**
```bash
pytest tests/integration/test_scholarships.py -v
```

## Next Steps

### Immediate Priorities
1. ✅ Complete Scholarships API testing
2. ✅ Complete Profiles API testing (including file uploads)
3. ✅ Complete Scholarship Tracking testing
4. ✅ Complete College Tracking testing

### Secondary Priorities
5. Complete Costs API testing
6. Complete Admissions API testing
7. Add unit tests for business logic
8. Add performance/load tests

### Future Enhancements
- CI/CD integration (GitHub Actions)
- Test data builders/factories
- API contract testing
- E2E tests with frontend
- Performance benchmarking

## Contributing

When adding tests:
1. Follow existing naming conventions
2. Use descriptive test names
3. Group related tests in classes
4. Add docstrings explaining what you're testing
5. Use appropriate fixtures
6. Test both happy paths and edge cases
7. Include authorization tests for protected endpoints

## Common Patterns

### Testing Protected Endpoints
```python
def test_protected_endpoint(self, client, auth_headers):
    # With auth - should succeed
    response = client.get("/api/v1/protected", headers=auth_headers)
    assert response.status_code == 200
    
    # Without auth - should fail
    response = client.get("/api/v1/protected")
    assert response.status_code in [401, 403]
```

### Testing Admin-Only Endpoints
```python
def test_admin_only(self, client, auth_headers, admin_headers):
    # Regular user - should fail
    response = client.post("/api/v1/admin", headers=auth_headers)
    assert response.status_code == 403
    
    # Admin user - should succeed
    response = client.post("/api/v1/admin", headers=admin_headers)
    assert response.status_code == 200
```

### Testing Pagination
```python
def test_pagination(self, client, db_session):
    # Create test data
    for i in range(10):
        create_test_record(db_session, i)
    
    # Test page 1
    response = client.get("/api/v1/resource?page=1&limit=5")
    data = response.json()
    assert len(data["items"]) == 5
    assert data["has_more"] is True
```

### Testing File Uploads
```python
def test_file_upload(self, client, auth_headers):
    files = {"file": ("test.pdf", b"file content", "application/pdf")}
    response = client.post(
        "/api/v1/upload",
        files=files,
        headers=auth_headers
    )
    assert response.status_code == 200
```

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
pg_isready

# Verify database exists
psql -l | grep magicscholar_test

# Check connection string
echo $DATABASE_URL
```

### Test Failures
```bash
# Run with verbose output
pytest tests/integration/test_failing.py -vv

# Show print statements
pytest tests/integration/test_failing.py -s

# Stop at first failure
pytest tests/ -x
```

### Fixture Issues
```bash
# See fixture setup/teardown
pytest tests/integration/test_file.py --setup-show
```

## Resources

- [MagicScholar OpenAPI Spec](../openapi.json)
- [Backend Routes](../Magic%20Scholar%20Routes)
- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## License

Proprietary - MagicScholar Project

---

**Last Updated:** November 19, 2025  
**Test Coverage:** 55 tests passing  
**Maintained By:** MagicScholar Development Team
