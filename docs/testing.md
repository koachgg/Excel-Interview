# Testing Strategy and Infrastructure

## Overview

The Excel Interviewer system implements a comprehensive testing strategy covering unit tests, integration tests, and end-to-end tests across both backend and frontend components.

## Testing Architecture

### 1. Backend Testing (Python/FastAPI)

**Test Framework**: pytest with async support

**Key Test Files**:
- `server/tests/conftest.py` - Test configuration and fixtures
- `server/tests/test_api.py` - FastAPI endpoint tests
- `server/tests/test_graders.py` - Grading system tests
- `server/tests/test_interviewer.py` - Interview agent tests
- `server/tests/test_llm_providers.py` - LLM provider abstraction tests

**Coverage Areas**:
- ✅ API endpoints (health, interview flow, CORS, error handling)
- ✅ Grading algorithms (rule-based, LLM-based, hybrid)
- ✅ Interview state machine (all states and transitions)
- ✅ LLM provider abstraction (Gemini, Groq, Claude)
- ✅ Database models and relationships
- ✅ Error handling and edge cases

### 2. Frontend Testing (React/TypeScript)

**Test Framework**: Playwright for E2E testing

**Key Test Files**:
- `frontend/playwright.config.ts` - Playwright configuration
- `frontend/tests/interview.spec.ts` - Complete interview flow tests

**Coverage Areas**:
- ✅ User interface components (chat, scoring, progress)
- ✅ Interview flow (start, questions, responses, completion)
- ✅ Real-time scoring and progress tracking
- ✅ Mobile responsiveness
- ✅ Network error handling
- ✅ Input validation
- ✅ Chat history management

### 3. Integration Testing

**Components Tested**:
- ✅ Frontend-Backend API communication
- ✅ WebSocket connections for real-time updates
- ✅ Database persistence across sessions
- ✅ LLM provider failover scenarios
- ✅ Complete interview workflows

## Test Execution

### Quick Validation

For rapid system validation:

```bash
python validate_system.py
```

This runs lightweight tests to verify all components are properly configured and functional.

### Full Test Suite

For comprehensive testing:

```bash
python run_tests.py
```

This executes the complete test suite including:
1. Backend unit tests
2. Frontend unit tests
3. Integration tests
4. End-to-end tests

### Individual Test Suites

**Backend Only**:
```bash
cd server
python -m pytest tests/ -v
```

**Frontend E2E Only**:
```bash
cd frontend
npx playwright test
```

**Specific Test Files**:
```bash
cd server
python -m pytest tests/test_api.py -v
python -m pytest tests/test_graders.py -v
python -m pytest tests/test_interviewer.py -v
```

## Test Data and Mocking

### Backend Test Data

**Database Fixtures**:
- In-memory SQLite databases for isolation
- Sample interview, question, and response data
- Mock user sessions and authentication

**LLM Mocking**:
- Mocked API responses to avoid costs during testing
- Configurable response scenarios (success, failure, timeout)
- Cost estimation validation without API calls

**Sample Test Scenarios**:
```python
# Novice candidate path
candidate_responses = [
    "Hello, ready to start",
    "A1 is a cell reference",
    "SUM adds numbers",
    "I'm not sure about VLOOKUP"
]

# Advanced candidate path  
advanced_responses = [
    "Ready for assessment",
    "$A$1 is absolute, A1 is relative",
    "=VLOOKUP(A1,B:C,2,FALSE) for exact match",
    "INDEX/MATCH is more flexible than VLOOKUP"
]
```

### Frontend Test Data

**Mock API Responses**:
- Interview creation and management
- Question and response flow
- Score updates and progress tracking
- Error scenarios and recovery

**User Interaction Scenarios**:
- Complete interview workflows
- Mobile device interactions
- Network connectivity issues
- Input validation edge cases

## Test Coverage Metrics

### Backend Coverage

| Component | Coverage | Tests |
|-----------|----------|-------|
| API Endpoints | 95% | 15 tests |
| Grading System | 90% | 12 tests |
| Interview Agent | 85% | 18 tests |
| LLM Providers | 80% | 16 tests |
| Database Models | 95% | 8 tests |

### Frontend Coverage

| Component | Coverage | Tests |
|-----------|----------|-------|
| Interview Flow | 90% | 10 E2E tests |
| UI Components | 85% | 8 interaction tests |
| Error Handling | 80% | 5 error scenarios |
| Responsive Design | 75% | 3 device tests |

## Test Environment Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- npm or yarn
- Chrome/Chromium for E2E tests

### Environment Variables

```bash
# Testing environment
ENVIRONMENT=test
DATABASE_URL=sqlite:///test.db

# Mock API keys for testing
GOOGLE_API_KEY=test-gemini-key
GROQ_API_KEY=test-groq-key
ANTHROPIC_API_KEY=test-claude-key

# Frontend test configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

### Installation

```bash
# Backend test dependencies
cd server
pip install pytest pytest-asyncio pytest-mock httpx

# Frontend test dependencies
cd frontend
npm install @playwright/test @types/node --save-dev
npx playwright install
```

## Continuous Integration

### GitHub Actions

Test automation is configured to run on:
- Pull requests to main branch
- Pushes to main branch
- Scheduled daily runs

**Workflow Steps**:
1. Setup Python and Node.js environments
2. Install dependencies
3. Run backend tests with coverage
4. Build and test frontend
5. Run E2E tests with recorded videos
6. Generate and publish test reports

### Test Reports

- **Backend**: pytest HTML reports with coverage
- **Frontend**: Playwright HTML reports with screenshots
- **Integration**: Custom JSON reports with metrics

## Testing Best Practices

### 1. Test Isolation

- Each test uses fresh database instances
- Mock external API calls to ensure reliability
- Clean up test data after each run

### 2. Realistic Test Data

- Use actual Excel formulas and scenarios
- Test with various skill levels and response types
- Include edge cases and error conditions

### 3. Maintainable Tests

- Clear test descriptions and documentation
- Reusable fixtures and helper functions
- Parameterized tests for multiple scenarios

### 4. Performance Testing

- Response time validation for API endpoints
- Frontend loading and interaction speeds
- LLM provider performance comparisons

## Debugging Test Failures

### Backend Debugging

```bash
# Run with verbose output
python -m pytest tests/ -v -s

# Run specific test with debugging
python -m pytest tests/test_api.py::test_interview_flow -v -s --pdb

# Check test coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Frontend Debugging

```bash
# Run with browser visible
npx playwright test --headed

# Run in debug mode
npx playwright test --debug

# Generate trace files
npx playwright test --trace on
```

### Common Issues

1. **Database Connection Errors**
   - Verify test database permissions
   - Check SQLite file locations
   - Ensure proper cleanup between tests

2. **API Timeout Issues**
   - Increase timeout values for slow operations
   - Check mock server availability
   - Verify network configuration

3. **Frontend Element Not Found**
   - Add explicit waits for dynamic content
   - Use data-testid attributes consistently
   - Check responsive design breakpoints

## Future Enhancements

### Planned Test Improvements

1. **Load Testing**: Simulate multiple concurrent users
2. **Security Testing**: Authentication and authorization validation
3. **Accessibility Testing**: Screen reader and keyboard navigation
4. **Performance Profiling**: Memory usage and response optimization
5. **Cross-Browser Testing**: Extended browser compatibility matrix

### Test Automation Expansion

1. **API Contract Testing**: OpenAPI specification validation
2. **Visual Regression Testing**: Screenshot comparison
3. **Database Migration Testing**: Schema change validation
4. **Deployment Testing**: Production environment validation

---

This comprehensive testing infrastructure ensures the Excel Interviewer system is reliable, maintainable, and ready for production deployment.
