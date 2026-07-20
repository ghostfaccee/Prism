from fastapi import status, APIRouter, Depends, Request
from app import get_auth_service, get_current_user
from app.schemas import UserRegister, UserLogin, TokenResponse, UserResponse
from app.services import AuthService

router = APIRouter()

@router.post('/auth/register', response_model = UserResponse, status_code = status.HTTP_201_CREATED, summary = 'Registration', description = 'Creates a new user. Returns the user_id, username and email (if email exists)')
async def register(request: Request, data: UserRegister, service: AuthService = Depends(get_auth_service)):
    return await service.register(data)

@router.post('/auth/login', response_model = TokenResponse, status_code = status.HTTP_200_OK, summary = 'Login', description = 'User login. Returns the jwt token required for other endpoints and its type.')
async def login(request: Request, data: UserLogin, service: AuthService = Depends(get_auth_service)):
    return await service.login(data)

