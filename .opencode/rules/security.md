# Security Rules

## General
- Never hardcode secrets, API keys, or credentials
- Validate all user input (never trust client data)
- Use parameterized queries to prevent SQL injection
- Implement proper authentication and authorization
- Follow least privilege principle for all access

## Web Security
- Set appropriate CORS headers
- Use HTTPS in production
- Implement CSRF protection
- Set security headers (X-Frame-Options, CSP, etc.)
- Sanitize all output to prevent XSS

## Data Protection
- Encrypt sensitive data at rest and in transit
- Hash passwords with bcrypt or argon2
- Implement proper session management
- Log security-relevant events
- Have a data breach response plan
