import pydantic


class BaseDto(pydantic.BaseModel):
    class Config:
        from_attributes = True
