from fastapi import status, APIRouter, Depends, Request
from uuid import UUID
from app.dependencies import get_current_user_id
from app import get_auth_service
from app.schemas import UserRegister, UserLogin, TokenResponse, UserResponse, RefreshTokenRequest
from app.services import AuthService
from app.middlewares import RateLimit

router = APIRouter()
limiter = RateLimit.get_limiter()

@router.post('/auth/register', response_model = UserResponse, status_code = status.HTTP_201_CREATED, summary = 'Registration', description = 'Creates a new user. Returns the user_id, username and email (if email exists).')
@limiter.limit('5/minute')
async def register(request: Request, data: UserRegister, service: AuthService = Depends(get_auth_service)):
    return await service.register(data)

@router.post('/auth/login', response_model = TokenResponse, status_code = status.HTTP_200_OK, summary = 'Login', description = 'User login. Returns the jwt token required for other endpoints and its type.')
@limiter.limit('5/minute')
async def login(request: Request, data: UserLogin, service: AuthService = Depends(get_auth_service)):
    return await service.login(data)

@router.post('/auth/refresh', response_model = TokenResponse, status_code = status.HTTP_200_OK, summary = 'Refresh access token', description = 'Allows the user to refresh the access token again, after which the refresh_token value becomes invalid and is added to the blacklist to protect against replay attacks. In addition, if signs of an attack appear, the token is deleted and refreshing the access token via this endpoint becomes impossible.')
@limiter.limit('5/minute')
async def refresh(request: Request, refresh_data: RefreshTokenRequest, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.refresh(refresh_data.refresh_token)

@router.post('/auth/logout', status_code = status.HTTP_204_NO_CONTENT, summary = 'Logout', description = 'Removes the refresh token from the database.')
@limiter.limit('5/minute')
async def logout(request: Request, current_user_id: UUID = Depends(get_current_user_id), auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.logout(current_user_id)