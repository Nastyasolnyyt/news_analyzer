from fastapi import APIRouter

from .auth.api import ROUTER as AUTH_ROUTER
from .entity.api import ROUTER as ENTITY_ROUTER
from .post.api import ROUTER as POST_ROUTER
from .users.api import ROUTER as USERS_ROUTER


def setup_core_routes() -> APIRouter:
    router = APIRouter()
    router.include_router(AUTH_ROUTER)
    router.include_router(USERS_ROUTER)
    router.include_router(POST_ROUTER, tags=["Post"])
    router.include_router(ENTITY_ROUTER, tags=["Entities"])

    return router
