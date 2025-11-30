from src.common import exc


class RepoError(exc.BaseError):
    """Error in repository."""

    default_msg = "Repository error"
    code = exc.ErrorCode.REPO


class NotFoundError(RepoError):
    """Object wasn't found."""

    default_msg = "Object wasn't found"
    code = exc.ErrorCode.REPO_NOT_FOUND


class QueryError(RepoError):
    """Error while executing query."""

    default_msg = "Error while executing query"
    code = exc.ErrorCode.REPO_QUERY


class SaveError(RepoError):
    """Error while saving."""

    default_msg = "Object save error"
    code = exc.ErrorCode.REPO_SAVE


class DeleteError(RepoError):
    """Error while deleting."""

    default_msg = "Object deletion error"
    code = exc.ErrorCode.REPO_DELETE
