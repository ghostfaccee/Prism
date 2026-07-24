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

## v0.2.0 - 22.07.2026
### Added
- email verification if the user specified their post when updating the data
- new endpoints (`/v1/me/password` - patch, `/v1/me` - patch | get, `/v1/user/username/{username}` - get, `/v1/user/uuid/{user_uuid}` - get)
### Notes
- now, if you didn't specify your location during registration, you can update your details and specify it there
- you can also update your password from the old one to the new one

## v0.2.1 - 23.07.2026
### Added & changed
- first e2e test for auth flow (registration and email verification)
- docker profiles have been added to run separate scripts (development and testing - `test`, production - `prod`)
- a test service for quick access to data that is only needed for testing
- the .env file has been updated and new environment variables have been added
### Notes
- you can view the launches of individual scripts in readme.md

## v0.2.2 - 24.07.2026
### Added
- unit tests for authorization and user
- fixed event loop pytest and asyncpg error

## to be continued :)
...