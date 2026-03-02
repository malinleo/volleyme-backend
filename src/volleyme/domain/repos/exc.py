import enum

from src.common import exc


class ErrorCode(enum.StrEnum):
    DEFAULT = "INFRA_ERROR"
    REPO = "REPO_ERROR"
    REPO_NOT_FOUND = "REPO_NOT_FOUND"
    REPO_SAVE = "REPO_SAVE_ERROR"
    REPO_DELETE = "REPO_DELETE_ERROR"
    REPO_QUERY = "REPO_QUERY_ERROR"


class RepoError(exc.BaseError):
    """Error in repository."""

    def __init__(self, detail: exc.ErrorDetail) -> None:
        super().__init__(detail=detail)


class QueryError(RepoError):
    """Error while executing query."""

    def __init__(self, query: str) -> None:
        super().__init__(
            detail=exc.ErrorDetail(
                code=ErrorCode.REPO_QUERY,
                messages=[f"Error while executing query\nQuery: {query}"],
            ),
        )


class NotFoundError(RepoError):
    """Object wasn't found."""

    def __init__(self, query: str) -> None:
        super().__init__(
            detail=exc.ErrorDetail(
                code=ErrorCode.REPO_NOT_FOUND,
                messages=[f"Object wasn't found\nQuery: {query}"],
            ),
        )


class SaveError(RepoError):
    """Error while saving."""

    def __init__(self, query: str) -> None:
        super().__init__(
            detail=exc.ErrorDetail(
                code=ErrorCode.REPO_SAVE,
                messages=[f"Object save error\nQuery: {query}"],
            ),
        )


class DeleteError(RepoError):
    """Error while deleting."""

    def __init__(self, query: str) -> None:
        super().__init__(
            detail=exc.ErrorDetail(
                code=ErrorCode.REPO_DELETE,
                messages=[f"Object deletion error\nQuery: {query}"],
            ),
        )
