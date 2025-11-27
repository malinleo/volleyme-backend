import pydantic_settings
import functools


class Settings(pydantic_settings.BaseSettings):
    PROJECT_NAME: str = "volleyme-backend"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # DB settings
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_DRIVER: str = "postgresql+asyncpg"

    @functools.cached_property
    def db_url(self) -> str:
        return f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()  # type: ignore
