from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_PATH = Path(__file__).parent.parent.parent.parent


# API Settings
class APIUrlsSettings(BaseModel):
    """Configure public urls."""

    docs: str = "/docs"
    re_doc: str = "/redoc"


class PublicApiSettings(BaseModel):
    """Configure public API settings."""

    name: str = "K1Core API"
    urls: APIUrlsSettings = APIUrlsSettings()


class DatabaseSettings(BaseModel):
    uri: str


class AccessTokenSettings(BaseModel):
    secret_key: str = "invalid"
    ttl: int = 3600  # seconds


# class RefreshTokenSettings(BaseModel):
#     secret_key: str = "invalid"
#     ttl: int = 100  # seconds


class AuthenticationSettings(BaseModel):
    access_token: AccessTokenSettings = AccessTokenSettings()
    # refresh_token: RefreshTokenSettings = RefreshTokenSettings()
    algorithm: str = "HS256"
    scheme: str = "Bearer"


class RabbitMQSettings(BaseModel):
    uri: str


class Settings(BaseSettings):
    """Application settings.
    django.conf.settings support value if started value uppercase.
    """

    DEBUG: bool = True
    ALLOWED_HOSTS: list[str] = ["*"]
    APP: str = "Backend"
    STATE: Literal["dev", "prod"] = "dev"
    SECRET_KEY: str
    ROOT_DIR: Path = ROOT_PATH
    SRC_DIR: Path = ROOT_PATH / "src"
    DATABASE: DatabaseSettings
    PUBLIC_API: PublicApiSettings = Field(default_factory=PublicApiSettings)
    AUTHENTICATION: AuthenticationSettings = AuthenticationSettings()
    BROKER: RabbitMQSettings

    model_config = SettingsConfigDict(
        env_file=ROOT_PATH / ".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        nested_model_default_partial_update=True,
    )


config = Settings()
