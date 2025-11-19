# Routes Remaining to Test - Quick Reference

## Summary
**Completed:** 55 tests (Auth + Institutions)  
**Remaining:** ~120+ tests across 6 major endpoint groups

---

## 1. Scholarships API (Priority: HIGH)
**Endpoint Prefix:** `/api/v1/scholarships/`

### Routes
```
POST   /api/v1/scholarships/                              Create scholarship (Admin)
GET    /api/v1/scholarships/                              Search/filter scholarships  
GET    /api/v1/scholarships/{scholarship_id}              Get single scholarship
PATCH  /api/v1/scholarships/{scholarship_id}              Update scholarship (Admin)
DELETE /api/v1/scholarships/{scholarship_id}              Delete scholarship (Admin)
GET    /api/v1/scholarships/list                          Simple list
GET    /api/v1/scholarships/upcoming-deadlines            Upcoming deadlines
POST   /api/v1/scholarships/bulk                          Bulk create (Admin)
```

### Key Test Scenarios
- ✓ CRUD with admin auth (create, read, update, delete)
- ✓ Search with query parameter
- ✓ Complex filtering:
  - scholarship_type (academic_merit, need_based, stem, arts, etc.)
  - active_only, verified_only, featured_only
  - min_amount, max_amount
  - renewable_only
  - min_gpa_filter
  - deadline_before, deadline_after
  - academic_year (YYYY-YYYY format)
- ✓ Sorting (created_at, amount_min, amount_max, deadline, title, views_count)
- ✓ Pagination
- ✓ Authorization (admin vs regular user)
- ✓ Bulk creation (max 100 per request)
- ✓ Data validation (amount ranges, dates, GPA format)

**Estimated Tests:** ~20-25 tests

---

## 2. Profiles API (Priority: HIGH)
**Endpoint Prefix:** `/api/v1/profiles/me/`

### Routes
```
GET    /api/v1/profiles/me                                Get current user profile
PUT    /api/v1/profiles/me                                Update profile
GET    /api/v1/profiles/me/matching-institutions          Get matching institutions
GET    /api/v1/profiles/me/settings                       Get user settings
PATCH  /api/v1/profiles/me/settings                       Update settings
POST   /api/v1/profiles/me/upload-headshot                Upload profile image
POST   /api/v1/profiles/me/upload-resume-and-update       Upload & parse resume
```

### Key Test Scenarios
- ✓ Profile CRUD operations
- ✓ File uploads:
  - Headshot (JPG, PNG, WEBP up to 5MB)
  - Resume (PDF, DOCX up to 10MB)
- ✓ Resume parsing integration (AI-powered)
- ✓ Matching institutions algorithm
- ✓ Settings management (confetti_enabled)
- ✓ Profile validation:
  - state (2-char), city, zip_code
  - graduation_year (2020-2035)
  - gpa (0.0-5.0), gpa_scale
  - sat_score (400-1600), act_score (1-36)
- ✓ Array fields:
  - extracurriculars (JSON array of objects)
  - work_experience (JSON array)
  - honors_awards (string array)
  - skills (string array)
- ✓ Profile auto-creation on user registration
- ✓ Authorization (user can only access their own profile)

**Estimated Tests:** ~18-22 tests

---

## 3. Scholarship Tracking (Priority: HIGH)
**Endpoint Prefix:** `/api/v1/scholarship-tracking/`

### Routes
```
GET    /api/v1/scholarship-tracking/dashboard                              Get dashboard
POST   /api/v1/scholarship-tracking/applications                           Save scholarship
GET    /api/v1/scholarship-tracking/applications                           List applications
GET    /api/v1/scholarship-tracking/applications/{id}                      Get application
PUT    /api/v1/scholarship-tracking/applications/{id}                      Update application
DELETE /api/v1/scholarship-tracking/applications/{id}                      Remove tracking
POST   /api/v1/scholarship-tracking/applications/{id}/mark-submitted       Mark submitted
POST   /api/v1/scholarship-tracking/applications/{id}/mark-accepted        Mark accepted
POST   /api/v1/scholarship-tracking/applications/{id}/mark-rejected        Mark rejected
```

### Key Test Scenarios
- ✓ Dashboard statistics:
  - total_applications, interested, planning, in_progress, submitted, accepted, rejected, not_pursuing
  - total_potential_value, total_awarded_value
  - upcoming_deadlines (next 30 days)
  - overdue applications
- ✓ Application status transitions:
  - interested → planning → in_progress → submitted → accepted/rejected/not_pursuing
- ✓ Automatic timestamp handling:
  - IN_PROGRESS sets started_at
  - SUBMITTED sets submitted_at
  - ACCEPTED/REJECTED sets decision_date
- ✓ Filtering & sorting:
  - Filter by status
  - Sort by deadline, amount, saved_at, status
  - Sort order (asc/desc)
- ✓ Quick action endpoints (mark-submitted, mark-accepted, mark-rejected)
- ✓ Award amount tracking
- ✓ Notes and essay drafts
- ✓ User data isolation (users can't see each other's tracking)
- ✓ Duplicate prevention

**Estimated Tests:** ~22-25 tests

---

## 4. College Tracking (Priority: HIGH)
**Endpoint Prefix:** `/api/v1/college-tracking/`

### Routes
```
GET    /api/v1/college-tracking/dashboard                                  Get dashboard
POST   /api/v1/college-tracking/applications                               Save college
GET    /api/v1/college-tracking/applications                               List applications
GET    /api/v1/college-tracking/applications/{id}                          Get application
PUT    /api/v1/college-tracking/applications/{id}                          Update application
DELETE /api/v1/college-tracking/applications/{id}                          Remove tracking
POST   /api/v1/college-tracking/applications/{id}/mark-submitted           Mark submitted
POST   /api/v1/college-tracking/applications/{id}/mark-accepted            Mark accepted
POST   /api/v1/college-tracking/applications/{id}/mark-rejected            Mark rejected
POST   /api/v1/college-tracking/applications/{id}/mark-waitlisted          Mark waitlisted
```

### Key Test Scenarios
- ✓ Dashboard statistics:
  - total_applications, submitted, in_progress, accepted, waitlisted, rejected, awaiting_decision
  - upcoming_deadlines (next 30 days)
  - overdue applications
- ✓ Application types:
  - early_decision, early_action, regular_decision, rolling
- ✓ Application status transitions:
  - researching → planning → in_progress → submitted → accepted/waitlisted/rejected/declined/enrolled
- ✓ Automatic timestamp handling:
  - IN_PROGRESS sets started_at
  - SUBMITTED sets submitted_at
  - ACCEPTED/WAITLISTED/REJECTED sets decided_at
- ✓ Decision date tracking (deadline vs actual_decision_date)
- ✓ Fee waiver management
- ✓ Application portal information (portal, portal_url, portal_username)
- ✓ Filtering & sorting:
  - Filter by status
  - Sort by deadline, saved_at, status
  - Sort order (asc/desc)
- ✓ Quick action endpoints (including waitlist)
- ✓ User data isolation
- ✓ Institution relationship (nested institution data)

**Estimated Tests:** ~24-28 tests

---

## 5. Costs API (Priority: MEDIUM)
**Endpoint Prefix:** `/api/v1/costs/`

### Routes
```
GET    /api/v1/costs/institution/{ipeds_id}                Get full cost data
GET    /api/v1/costs/institution/{ipeds_id}/summary        Cost summary
GET    /api/v1/costs/compare                               Compare costs (multiple institutions)
```

### Key Test Scenarios
- ✓ Cost data retrieval (tuition, fees, room & board)
- ✓ In-state vs out-of-state residency parameter
- ✓ Cost summaries for card displays
- ✓ Multi-institution comparison (query param: ipeds_ids=102580,103501,442523)
- ✓ Most recent year selection
- ✓ Invalid IPEDS ID handling (404)
- ✓ Missing cost data scenarios (institutions without cost data)
- ✓ Validation of IPEDS ID format

**Estimated Tests:** ~10-12 tests

---

## 6. Admissions API (Priority: MEDIUM)
**Endpoint Prefix:** `/api/v1/admissions/`

### Routes
```
GET    /api/v1/admissions/institution/{ipeds_id}                          Latest data
GET    /api/v1/admissions/institution/{ipeds_id}/all                      All years
GET    /api/v1/admissions/institution/{ipeds_id}/year/{academic_year}    Specific year
```

### Key Test Scenarios
- ✓ Latest admissions data retrieval
- ✓ All years retrieval (ordered by year, newest first)
- ✓ Specific academic year retrieval (format: "2023-24" or "2023-2024")
- ✓ Admissions statistics:
  - applications_total, admissions_total, enrolled_total
  - acceptance_rate, yield_rate
  - SAT ranges (reading & math: 25th, 50th, 75th percentile)
  - percent_submitting_sat
- ✓ Invalid IPEDS ID handling
- ✓ Missing admissions data (404)
- ✓ Invalid academic year format
- ✓ Historical trend analysis

**Estimated Tests:** ~12-15 tests

---

## 7. System Routes (Priority: LOW)
**No auth required**

### Routes
```
GET    /                                                   Root endpoint
GET    /health                                             Health check
GET    /routes-simple                                      Route listing
```

### Key Test Scenarios
- ✓ Root returns welcome message
- ✓ Health check returns status
- ✓ Routes simple returns text list of routes

**Estimated Tests:** ~3 tests

---

## Explicitly Excluded (Local Testing)

### OAuth Routes
```
GET    /api/v1/oauth/google/url                           (Not testing locally)
GET    /api/v1/oauth/google/callback                      (Not testing locally)
GET    /api/v1/oauth/linkedin/url                         (Not testing locally)
GET    /api/v1/oauth/linkedin/callback                    (Not testing locally)
DELETE /api/v1/oauth/cleanup-expired-states               (Not testing locally)
```

**Reason:** Testing locally without OAuth provider configuration

---

## Testing Order Recommendation

### Week 1: Core User Features
1. **Scholarships API** (~20-25 tests)
   - Most complex filtering logic
   - Admin authorization patterns
2. **Profiles API** (~18-22 tests)
   - File uploads
   - Resume parsing

### Week 2: Application Tracking
3. **Scholarship Tracking** (~22-25 tests)
   - Status transitions
   - Dashboard logic
4. **College Tracking** (~24-28 tests)
   - Similar patterns to scholarship tracking
   - Additional status (waitlisted)

### Week 3: Data & Polish
5. **Costs API** (~10-12 tests)
   - Simpler endpoint group
6. **Admissions API** (~12-15 tests)
   - Similar patterns to costs
7. **System Routes** (~3 tests)
   - Quick wins

---

## Total Test Estimate

| Endpoint Group        | Tests | Priority |
|-----------------------|-------|----------|
| Authentication        | 24 ✅ | HIGH     |
| Institutions          | 31 ✅ | HIGH     |
| Scholarships          | ~22   | HIGH     |
| Profiles              | ~20   | HIGH     |
| Scholarship Tracking  | ~24   | HIGH     |
| College Tracking      | ~26   | HIGH     |
| Costs                 | ~11   | MEDIUM   |
| Admissions            | ~13   | MEDIUM   |
| System                | ~3    | LOW      |
| **TOTAL**             | **~174** | -     |

**Current Progress: 55/174 (32%)**

---

## Key Patterns to Test

### 1. Authorization Patterns
```python
# Protected endpoint (user auth required)
response = client.get("/api/v1/profiles/me", headers=auth_headers)

# Admin-only endpoint
response = client.post("/api/v1/scholarships/", json=data, headers=admin_headers)

# User data isolation
# User A cannot access User B's tracked scholarships
```

### 2. Pagination & Filtering
```python
# Complex filtering
params = {
    "scholarship_type": "stem",
    "min_amount": 5000,
    "min_gpa_filter": 3.5,
    "deadline_after": "2025-10-01",
    "sort_by": "amount_max",
    "sort_order": "desc"
}
response = client.get("/api/v1/scholarships/", params=params)
```

### 3. File Uploads
```python
files = {"file": ("resume.pdf", pdf_content, "application/pdf")}
response = client.post(
    "/api/v1/profiles/me/upload-resume-and-update",
    files=files,
    headers=auth_headers
)
```

### 4. Status Transitions
```python
# Create tracking entry
response = client.post("/api/v1/scholarship-tracking/applications", json=data)
app_id = response.json()["id"]

# Transition through statuses
client.put(f"/api/v1/scholarship-tracking/applications/{app_id}", 
          json={"status": "in_progress"})

# Quick action
client.post(f"/api/v1/scholarship-tracking/applications/{app_id}/mark-submitted")

# Verify timestamps updated correctly
```

### 5. Dashboard Aggregations
```python
response = client.get("/api/v1/scholarship-tracking/dashboard", headers=auth_headers)
data = response.json()

# Verify summary statistics
assert data["summary"]["total_applications"] == expected_count
assert data["summary"]["total_potential_value"] == expected_value

# Verify upcoming deadlines calculated correctly
assert len(data["upcoming_deadlines"]) == expected_upcoming_count
```

---

## Next Steps

1. ✅ Start with **Scholarships API** (foundation for tracking)
2. ✅ Move to **Profiles API** (needed for matching & resume features)
3. ✅ Test **Scholarship Tracking** (builds on scholarships)
4. ✅ Test **College Tracking** (similar to scholarship tracking)
5. Complete **Costs** and **Admissions** (data retrieval)
6. Add **System Routes** (quick wins for 100% coverage)

---

**Generated:** November 19, 2025  
**For:** MagicScholar Testing Repository
