# API package 
from fastapi import APIRouter
from app.api import auth, incidents, units, logs

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(units.router, prefix="/units", tags=["units"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"]) 