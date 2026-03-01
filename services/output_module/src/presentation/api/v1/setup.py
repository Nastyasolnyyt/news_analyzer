from fastapi import APIRouter
from src.presentation.api.v1.routes.setup import setup_core_routes


def setup_v1_routes() -> APIRouter:
    router = APIRouter(prefix="/v1")
    router.include_router(setup_core_routes())
    return router
