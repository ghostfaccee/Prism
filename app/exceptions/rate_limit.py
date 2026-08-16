from fastapi import HTTPException, status

class RateLimitExceedError(HTTPException):
    def __init__(self):
        return super().__init__(status.HTTP_429_TOO_MANY_REQUESTS, 'Too many requests. Please try again later.')