# Testing Rules

## Test Types
- Unit tests: Test individual functions and classes in isolation
- Integration tests: Test component interactions
- E2E tests: Test complete user workflows
- Property tests: Test invariants and edge cases

## Python Testing
- Use pytest as the test framework
- Use pytest-cov for coverage reporting
- Name tests descriptively: test_<function>_<scenario>_<expected>
- Use fixtures for test setup and teardown
- Parametrize tests to cover multiple cases
- Mock external services and I/O operations

## JavaScript Testing
- Use vitest or jest for unit tests
- Use @playwright/test for browser tests
- Test component behavior, not implementation details
