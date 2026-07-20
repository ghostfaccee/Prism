from fastapi import HTTPException, status

class UsernameExistsError(HTTPException):
    def __init__(self, username: str):
        return super().__init__(status.HTTP_400_BAD_REQUEST, f'Username \"{username}\" already taken')

class EmailExistsError(HTTPException):
    def __init__(self, email: str):
        return super().__init__(status.HTTP_400_BAD_REQUEST, f'Email \"{email}\" already registered')

class UsernameDoesNotExistsError(HTTPException):
    def __init__(self, username: str):
        return super().__init__(status.HTTP_401_UNAUTHORIZED, f'Username \"{username}\" does not exists')

class InvalidPassword(HTTPException):
    def __init__(self):
        return super().__init__(status.HTTP_401_UNAUTHORIZED, 'Invalid password')

class UserDoesNotExists(HTTPException):
    def __init__(self):
        return super().__init__(status.HTTP_400_BAD_REQUEST, 'User does not exists')

class CouldNotValidateCredentialsError(HTTPException):
    def __init__(self):
        return super().__init__(status.HTTP_401_UNAUTHORIZED, 'Could not validate credentials', {'WWW-Authenticate': 'Bearer'})
    