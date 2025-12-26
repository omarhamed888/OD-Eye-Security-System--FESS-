from fastapi import APIRouter
from app.api.v1.endpoints import auth, cameras, alerts, stream

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(cameras.router, prefix="/cameras", tags=["cameras"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(stream.router, tags=["stream"])
