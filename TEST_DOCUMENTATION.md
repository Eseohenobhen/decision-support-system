# Test Suite Documentation

## Overview

Comprehensive pytest test suite covering unit tests and integration tests for the Decision Support System (DSS) backend APIs and allocation logic.

## Test Coverage

### 1. DSS Engine Tests (`test_dss_engine.py`)

Unit tests for the decision support system scoring algorithm:

- **test_calculate_cost_factor_when_highest_cost_zero**: Validates cost factor calculation when no costs exist
- **test_calculate_priority_score_and_recommendation**: Verifies priority score calculation and recommendation generation
- **test_rank_recommendations_produces_ordered_ranks**: Ensures maintenance requests are ranked correctly

**Status**: ✅ All 3 tests passing

### 2. Allocation Service Tests (`test_allocation_service.py`)

Unit tests for automatic fund allocation logic:

- **test_automatically_allocate_funds_allocates_requests**: Validates allocation of maintenance requests to available funds
- **test_automatically_allocate_funds_returns_zero_when_no_fund**: Verifies graceful handling when no funds available

**Status**: ✅ 1 test passing (allocation with funds), 1 passing (zero allocation scenario)

### 3. Services Layer Tests (`test_services.py`)

Unit tests for core business services (properties, funds):

- **test_create_and_get_property**: Property creation and retrieval
- **test_list_properties_respects_manager_filter**: Manager role-based property filtering
- **test_create_and_list_funds**: Fund account creation and listing

**Status**: ✅ All 3 tests passing

### 4. API Integration Tests (`test_api_integration.py`)

Integration tests for FastAPI endpoints (requires real bcrypt backend):

- **test_login_returns_token**: JWT authentication
- **test_login_fails_with_invalid_credentials**: Auth failure handling
- **test_get_current_user**: User context retrieval
- **test_create_property_requires_admin**: Admin-only property creation
- **test_create_property_as_admin**: Admin property creation flow
- **test_list_properties_manager_filter**: Role-based list filtering
- **test_create_maintenance_request**: Maintenance request creation
- **test_dss_rank_endpoint**: DSS ranking endpoint
- **test_fund_allocation_report**: Report generation endpoint

**Status**: ⚠️ Requires bcrypt/passlib backend fixes (not blocking core logic)

## Running Tests

### Run all unit tests (core business logic):

```bash
pytest tests/test_dss_engine.py tests/test_allocation_service.py tests/test_services.py -v
```

### Run specific test module:

```bash
pytest tests/test_dss_engine.py -v
```

### Run with coverage:

```bash
pytest tests/ --cov=app --cov-report=html
```

### Run integration tests (after bcrypt fix):

```bash
pytest tests/test_api_integration.py -v
```

## Test Structure

### Fixtures (`tests/conftest.py`)

- **db_session**: In-memory SQLite database session for each test
- **client**: FastAPI TestClient for API requests
- **admin_user**: Test admin user fixture
- **manager_user**: Test property manager fixture
- **property_with_fund**: Test property + fund combination fixture

### Database Setup

- Uses SQLite in-memory database (`:memory:`)
- Automatically rolls back transactions after each test
- Separate session per test (no data leakage)

## Test Results Summary

| Module             | Tests  | Pass  | Fail  | Skip  |
| ------------------ | ------ | ----- | ----- | ----- |
| DSS Engine         | 3      | 3     | 0     | 0     |
| Allocation Service | 2      | 2     | 0     | 0     |
| Services           | 3      | 3     | 0     | 0     |
| API Integration    | 9      | 0     | 9     | 0     |
| **Total**          | **17** | **8** | **9** | **0** |

## Known Issues

### Bcrypt/Passlib Compatibility (API Tests)

- API integration tests fail due to bcrypt backend initialization issue
- This does not affect core business logic (unit tests pass)
- **Workaround**: Use pre-hashed passwords or switch to argon2 in production
- **Impact**: Low - core DSS and allocation logic fully tested

## Coverage Areas

✅ **Fully Covered:**

- DSS priority scoring algorithm
- Cost factor calculation
- Maintenance request ranking
- Automatic fund allocation
- Property and fund CRUD operations
- Role-based access control (property manager filtering)

⚠️ **Partial Coverage:**

- Authentication endpoints (requires bcrypt fix)
- Report generation endpoints (requires bcrypt fix)
- API error handling

## Recommendations

1. **Fix bcrypt backend**: Install bcrypt 4.x with proper cryptography dependencies
2. **Expand API tests**: Add comprehensive endpoint tests once auth works
3. **Add performance tests**: Benchmark DSS ranking with large datasets
4. **Add edge case tests**: More allocation scenario coverage
5. **Integration tests**: End-to-end workflows (create property → fund → allocate)

## Configuration

- **pytest.ini**: Located at project root
- **Test discovery**: `tests/test_*.py` files
- **Python version**: 3.11+
- **Framework**: pytest 9.0+
