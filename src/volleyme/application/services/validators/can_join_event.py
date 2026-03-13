import dataclasses

from src.common import usecases as common_usecases
from src.volleyme.domain import aggregates, types


@dataclasses.dataclass(frozen=True)
class CanJoinEventValidator(common_usecases.Validator):
    user_id: types.UserId
    event: aggregates.Event
    invitation: aggregates.EventInvitation | None

    def validate(self) -> common_usecases.ValidationResult:
        if self.event.is_public:
            return common_usecases.ValidationResult(is_valid=True)
        if not self.invitation:
            return common_usecases.ValidationResult(is_valid=False)
        return common_usecases.ValidationResult(is_valid=True)
