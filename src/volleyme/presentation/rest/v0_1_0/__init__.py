import fastapi

from . import deps as deps
from .endpoints import auth_router as auth_router
from .endpoints import events_router as events_router
from .endpoints import invitation_router as invitation_router

v0_1_0_router = fastapi.APIRouter(prefix="/0.1.0", tags=["0.1.0"])
v0_1_0_router.include_router(auth_router)
v0_1_0_router.include_router(events_router)
v0_1_0_router.include_router(invitation_router)
