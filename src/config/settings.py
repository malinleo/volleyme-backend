import functools
import pathlib

import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    PROJECT_NAME: str = "volleyme-backend"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent.parent

    # DB settings
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_DRIVER: str = "postgresql+asyncpg"

    # RabbitMQ settings
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str

    JWT_PUBLIC_KEY_PATH: pathlib.Path = BASE_DIR / ".jwt" / "jwtRS256.key.pub"
    JWT_PRIVATE_KEY_PATH: pathlib.Path = BASE_DIR / ".jwt" / "jwtRS256.key"
    JWT_ALGORITHM: str = "RS256"

    ACCESS_TOKEN_EXPIRES_IN: int = 24 * 60 * 60  # 1 day in seconds
    REFRESH_TOKEN_EXPIRES_IN: int = 7 * 24 * 60 * 60  # 7 days in seconds

    _jwt_public_key: str | None = None
    _jwt_private_key: str | None = None

    # Pagination settings
    DEFAULT_PAGE_SIZE: int = 25
    MAX_PAGE_SIZE: int = 100

    # Password settings
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_MAX_LENGTH: int = 100

    # Event invitation settings
    EVENT_INVITATION_EXPIRATION_SECONDS: int = 1 * 24 * 60 * 60  # 1 day in seconds

    # Events settings
    OUTBOX_BIG_POLL_INTERVAL_SECONDS: float = 3.0
    OUTBOX_SMALL_POLL_INTERVAL_SECONDS: float = 0.5
    OUTBOX_POLL_BATCH_SIZE: int = 100
    OUTBOX_ROUTING_KEY: str = "outbox"
    EVENTS_POLL_INTERVAL_SECONDS: float = 1.0
    EVENTS_TIMEOUT_SECONDS: float = 10.0
    EVENTS_QUEUE_NAME: str = "events"

    model_config = pydantic_settings.SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @functools.cached_property
    def db_url(self) -> str:
        return f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def jwt_public_key(self) -> str:
        if not self._jwt_public_key:
            with open(self.JWT_PUBLIC_KEY_PATH, "r") as jwt_public_key_file:
                self._jwt_public_key = jwt_public_key_file.read()
        return self._jwt_public_key

    @property
    def jwt_private_key(self) -> str:
        if not self._jwt_private_key:
            with open(self.JWT_PRIVATE_KEY_PATH, "r") as jwt_private_key_file:
                self._jwt_private_key = jwt_private_key_file.read()
        return self._jwt_private_key

    @property
    def rabbitmq_url(self) -> str:
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}"


settings = Settings()  # type: ignore
