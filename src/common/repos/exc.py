from src.common import exc


class RepoError(exc.BaseError):
    """Error in repository."""

    default_msg = "Repository error"


class NotFoundError(RepoError):
    """Object wasn't found."""

    default_msg = "Object wasn't found"


class QueryError(RepoError):
    """Error while executing query."""

    default_msg = """Error while executing query."""


class SaveError(RepoError):
    """Error while saving."""

    default_msg = "Error during saving"


class DeleteError(RepoError):
    """Error while deleting."""

    default_msg = "Error during deletion"
