import dataclasses

from src.common import usecases as common_usecases
from src.volleyme.domain import aggregates, types


@dataclasses.dataclass(frozen=True)
class CanJoinEventValidator(common_usecases.Validator):
    user_id: types.UserId
    event: aggregates.Event

    def validate(self) -> common_usecases.ValidationResult:
        if self.event.is_started:
            return common_usecases.ValidationResult(
                is_valid=False,
                error_msg="Event is already started",
            )
        if self.event.max_participants_count <= len(self.event.participants):
            return common_usecases.ValidationResult(
                is_valid=False,
                error_msg="Event is already full",
            )
        if self.user_id in self.event.participants:
            return common_usecases.ValidationResult(
                is_valid=False,
                error_msg="You are already a participant of the event",
            )
        return common_usecases.ValidationResult(is_valid=True)
