from pydantic import BaseModel

class VerificationResponse(BaseModel):
    detail: str = 'Email verified successfully'
