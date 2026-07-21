from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_verification_service, get_current_user
from app.schemas import VerificationResponse

router = APIRouter()

@router.get('/verify/{token}', response_model = VerificationResponse, status_code = status.HTTP_200_OK, summary = 'Verification link', description = 'The email will contain a link to confirm your email. This link contains a token that is required to confirm your user account. You must be a registered user with a jwt token before you can verify your email.')
async def verify_user(request: Request, token: str, service = Depends(get_verification_service), user = Depends(get_current_user)):
    return await service.verify_email(token)
