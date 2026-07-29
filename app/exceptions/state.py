from fastapi import HTTPException, status

class InvalidStateError(HTTPException):
    def __init__(self):
        return super().__init__(status.HTTP_400_BAD_REQUEST, 'Invalid state parameter. Possible CSRF attack.')

class StateExpiredError(HTTPException):
    def __init__(self):
        return super().__init__(status.HTTP_400_BAD_REQUEST, 'State expired. Please try again.')
    