from fastapi import APIRouter
from app.api.v1.endpoints.auth import router as auth_router

router = APIRouter()

@router.get('/')
async def main_page():
    return {'detail': 'Welcome to Prism :)'}

router.include_router(auth_router)