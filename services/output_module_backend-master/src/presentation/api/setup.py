from fastapi import APIRouter, FastAPI
from src.presentation.api.v1.setup import setup_v1_routes


def setup_routes(app: FastAPI) -> None:
    router = APIRouter(prefix="/api")
    router.include_router(setup_v1_routes())
    app.include_router(router)
