from fastapi import APIRouter, Depends, status, Request
from app import get_verification_service, get_current_user
from app.schemas import VerificationResponse
from app.services import VerificationService
from app.models import User
from app.middlewares import RateLimit

router = APIRouter()
limiter = RateLimit.get_limiter()

@router.get('/verify/{token}', response_model = VerificationResponse, status_code = status.HTTP_200_OK, summary = 'Verification link', description = 'The email will contain a link to confirm your email. This link contains a token that is required to confirm your user account. You must be a registered user with a jwt token before you can verify your email. Requires a jwt token.')
@limiter.limit('5/minute')
async def verify_user(request: Request, token: str, service: VerificationService = Depends(get_verification_service), current_user: User = Depends(get_current_user)):
    return await service.verify_email(token)
