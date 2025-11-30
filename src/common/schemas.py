import pydantic


class BaseSchema(pydantic.BaseModel):
    """Base schema for all schemas."""

    class Config:
        from_attributes = True
