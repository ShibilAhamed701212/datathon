# Coding Rules

## General
- Write clean, readable, maintainable code
- Follow the principle of least surprise
- Prefer simplicity over complexity
- Optimize for readability first, performance second
- Add type hints to all function signatures (Python, TypeScript)
- Use meaningful variable and function names
- Keep functions small and focused (single responsibility)

## Python
- Follow PEP 8 style guide
- Use type hints for all function parameters and return values
- Use async/await for I/O-bound operations
- Prefer dataclasses over dicts for structured data
- Use pathlib over os.path for file operations
- Write docstrings for public APIs (Google style)
- Use pytest for all tests

## Error Handling
- Handle errors gracefully with specific exception types
- Log errors with context, not just messages
- Never swallow exceptions silently
- Use structured logging over print statements
- Implement proper input validation at boundaries

## Testing
- Write tests alongside implementation
- Aim for >80% test coverage on critical paths
- Test edge cases and error conditions
- Use descriptive test names (test_when_condition_then_result)
- Prefer property-based testing where appropriate
