# Changelog

## v0.1.0 - 21.07.2026
### Added
- jwt-authentication (registration, login)
- email-verification via celery + redis
- custom exceptions for authentication errors

### Notes
- verification works only if user provided email during registration
- celery worker is running separately via docker compose
- smtp is configured via gmail (app password required)

## to be continued :)
...