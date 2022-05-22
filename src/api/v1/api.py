from fastapi import APIRouter

from api.v1.endpoints import login, user

api_router = APIRouter()
api_router.include_router(login.router, tags=["Auth"])
api_router.include_router(user.router, tags=["User"])
