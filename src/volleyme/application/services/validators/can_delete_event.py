import dataclasses

from src.common import usecases as common_usecases
from src.volleyme.domain import aggregates, types


@dataclasses.dataclass(frozen=True)
class CanDeleteEventValidator(common_usecases.Validator):
    user_id: types.UserId
    event: aggregates.Event

    def validate(self) -> common_usecases.ValidationResult:
        if self.event.is_started:
            return common_usecases.ValidationResult(
                is_valid=False,
                error_msg="Event is already started",
            )
        if self.event.created_by != self.user_id:
            return common_usecases.ValidationResult(
                is_valid=False,
                error_msg="You are not allowed to delete this event",
            )
        return common_usecases.ValidationResult(is_valid=True)
