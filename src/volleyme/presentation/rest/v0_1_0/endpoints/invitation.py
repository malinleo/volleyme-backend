import typing

import fastapi
from dependency_injector import wiring

from src.volleyme import di
from src.volleyme.application import usecases
from src.volleyme.presentation.rest.v0_1_0 import deps, schemas

invitation_router = fastapi.APIRouter(
    prefix="/invitations",
    dependencies=[fastapi.Depends(deps.authenticate_user)],
)


@invitation_router.post("/", response_model=schemas.InvitationDetailSchema)
@wiring.inject
async def invite_to_event(
    usecase: typing.Annotated[
        usecases.InviteToEventUseCase,
        fastapi.Depends(wiring.Closing[wiring.Provide[di.DI.usecases.invite_to_event]]),
    ],
    user: deps.AuthUserDependencyType,
    invitation_data: schemas.InvitationCreateSchema,
):
    return schemas.InvitationDetailSchema.model_validate(
        await usecase.execute(
            event_id=invitation_data.event_id,
            user_id=user.id,
        ),
    )
