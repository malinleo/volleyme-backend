import fastapi

from . import deps as deps
from .endpoints import auth_router as auth_router
from .endpoints import events_router as events_router
from .endpoints import invitation_router as invitation_router

v1_router = fastapi.APIRouter(prefix="/v1", tags=["v1"])
v1_router.include_router(auth_router)
v1_router.include_router(events_router)
v1_router.include_router(invitation_router)
