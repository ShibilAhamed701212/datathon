# Architecture Rules

## Design Principles
- Follow SOLID principles
- Prefer composition over inheritance
- Design for testability from the start
- Keep dependencies explicit and minimal
- Separate concerns: presentation, business logic, data access
- Use dependency injection for loose coupling

## Project Structure
- Organize by feature, not by layer
- Keep related code close together
- Use clear naming conventions for modules
- Maintain a flat structure where possible

## API Design
- Follow RESTful conventions for HTTP APIs
- Use consistent error response formats
- Version APIs from day one
- Document all endpoints with OpenAPI/Swagger
- Implement proper rate limiting and authentication

## Data
- Define clear data ownership boundaries
- Use migrations for schema changes
- Keep database queries simple and indexed
- Use transactions for atomic operations
- Implement data validation at every layer
