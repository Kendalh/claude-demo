# 🧪 PagerDuty Incident Analytics Dashboard - Test Suite

This directory contains comprehensive unit tests for all components of the PagerDuty Incident Analytics Dashboard.

## 🚀 Quick Start

### Run All Tests with Summary Report
```bash
# From the pagerduty/ directory
python3 run_tests.py
```

### Manual Test Execution
```bash
# Install test dependencies
pip3 install -r test/test_requirements.txt

# Run all tests
python3 -m pytest test/ -v

# Run tests with coverage
python3 -m pytest test/ --cov=. --cov-report=html --cov-report=term-missing
```

## 📁 Test Structure

```
test/
├── README.md                    # This file
├── conftest.py                  # Pytest configuration and shared fixtures
├── test_requirements.txt       # Test dependencies
├── test_incident_v2.py         # Data model tests (17 tests)
├── test_database_v2.py         # Database layer tests (19 tests)
├── test_pagerduty_client_v2.py # API client tests (25 tests)
├── test_analytics_v2.py        # Analytics layer tests (26 tests)
├── test_app_v2.py              # Flask web application tests (25 tests)
└── fixtures/
    ├── sample_pagerduty_data.py # Mock PagerDuty API responses
    └── test_database.py         # Test database utilities
```

## 🧪 Test Categories

### **✅ Data Model Tests** (`test_incident_v2.py`)
- Incident object creation and validation
- Serialization/deserialization (`to_dict`, `from_dict`)
- Timezone handling (UTC-7 conversions)
- Status checking methods
- Edge cases and error conditions

### **✅ Database Tests** (`test_database_v2.py`)
- SQLite database initialization
- CRUD operations (Create, Read, Update, Delete)
- Batch operations and performance
- Date range filtering
- Schema migration and indexing

### **✅ API Client Tests** (`test_pagerduty_client_v2.py`)
- PagerDuty API integration (mocked)
- Service configuration loading
- Incident fetching and parsing
- Escalation detection logic
- Custom fields processing
- Error handling and retries

### **✅ Analytics Tests** (`test_analytics_v2.py`)
- Metrics calculation and aggregation
- Service-specific analytics
- Time-based filtering
- Escalation rate calculations
- CCOE resolution tracking

### **✅ Web Application Tests** (`test_app_v2.py`)
- Flask route testing
- JSON API endpoints
- Error handling
- Service configuration
- Calendar data generation

## 🔧 Testing Features

### **Advanced Testing Techniques**
- **🔧 HTTP Mocking**: PagerDuty API responses with `responses` library
- **💾 Database Isolation**: Temporary SQLite databases for each test
- **⏰ Time Mocking**: Timezone testing with `freezegun`
- **📊 Fixtures**: Realistic sample data and reusable test utilities
- **🛡️ Edge Cases**: Error conditions, timeouts, malformed data

### **Test Data**
- **Mock API Responses**: Realistic PagerDuty incident data
- **Sample Incidents**: Various states (triggered, escalated, resolved)
- **Timezone Scenarios**: UTC-7 conversion testing
- **Error Conditions**: Network failures, malformed responses

## 📊 Current Test Status

| Component | Tests | Pass Rate | Coverage |
|-----------|-------|-----------|----------|
| **Incident Model** | 17 | 100% ✅ | 100% |
| **Database Layer** | 19 | 79% ⚠️ | 64% |
| **API Client** | 25 | 68% ⚠️ | 81% |
| **Analytics** | 26 | 46% ❌ | 61% |
| **Web App** | 25 | 68% ⚠️ | 85% |
| **Overall** | **112** | **71%** | **65%** |

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Make sure you're in the pagerduty/ directory
cd /path/to/pagerduty/
python3 -m pytest test/
```

**Missing Dependencies**
```bash
pip3 install -r test/test_requirements.txt
pip3 install pytest-cov
```

**Database Lock Errors**
```bash
# Tests use temporary databases, but if you see lock errors:
rm -f *.db test/*.db
```

### Running Specific Tests
```bash
# Single test file
python3 -m pytest test/test_incident_v2.py -v

# Single test method
python3 -m pytest test/test_incident_v2.py::TestIncidentDataModel::test_incident_initialization -v

# With coverage for specific module
python3 -m pytest test/test_incident_v2.py --cov=incident_v2 --cov-report=term-missing
```

## 🎯 Contributing

When adding new features:

1. **Write tests first** (TDD approach)
2. **Follow naming conventions**: `test_feature_description`
3. **Use fixtures** for common test data
4. **Mock external dependencies** (API calls, file I/O)
5. **Test edge cases** (empty data, errors, timeouts)
6. **Update this README** if adding new test categories

### Test Writing Guidelines
```python
def test_feature_description(self, fixture_name):
    """Test description explaining what this test validates"""
    # Arrange - Set up test data
    # Act - Execute the code being tested
    # Assert - Verify the results
```

## 📚 Dependencies

### Test Framework
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities

### Testing Libraries
- `responses` - HTTP request mocking
- `freezegun` - Time/date mocking
- `unittest.mock` - Python standard mocking

### Application Dependencies
- All production dependencies from `requirements.txt`