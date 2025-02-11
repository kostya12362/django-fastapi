from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from pydantic import ConfigDict, EmailStr, ValidationError, model_validator

from core.schemas import PublicSchema


class UserSingInSchema(PublicSchema):
    username: str
    password: str


class UserSingUpSchema(UserSingInSchema):
    email: Optional[EmailStr] = None
    password_re: str
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "kostay12362",
                "email": "rota@gmail.com",
                "password": "Admin123_",
                "password_re": "Admin123_",
            }
        }
    )

    @model_validator(mode="after")
    def passwords_match(self) -> Any:
        if self.password != self.password_re:
            raise ValidationError(_("Passwords don't match"))
        return self


class TokenSchemaResponse(PublicSchema):
    access_token: str
    token_type: str
    access_token_expires: float

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJ...",
                "token_type": settings.AUTHENTICATION.scheme,
                "access_token_expires": settings.AUTHENTICATION.access_token.ttl,
            }
        }
    )


class BaseUserResponseSchema(PublicSchema):
    id: UUID
    model_config = ConfigDict(
        json_schema_extra={"example": {"id": "d290f1ee-6c54-4b01-90e6-d701748f0851"}}
    )


class UserResponseSchema(BaseUserResponseSchema):
    id: UUID
    username: str
    email: Optional[EmailStr] = None
    is_active: bool
    is_staff: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "username": "kostay12362",
                "email": "test@gmail.com",
                "is_active": True,
                "is_staff": False,
                "is_superuser": False,
                "created_at": "2021-09-14T15:00:00",
                "last_login": "2021-09-14T15:00:00",
            }
        }
    )
