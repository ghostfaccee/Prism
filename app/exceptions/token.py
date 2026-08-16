from fastapi import HTTPException, status

class TokenNotFoundError(HTTPException):
    def __init__(self):
        return super().__init__(status.HTTP_400_BAD_REQUEST, 'Token not found')