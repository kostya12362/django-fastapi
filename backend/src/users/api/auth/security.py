from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

import jwt
from django.conf import settings
from django.contrib.auth import aauthenticate
from fastapi import Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from jwt.exceptions import InvalidTokenError

from core.schemas import HTTPException
from users.api.schemas import TokenSchemaResponse
from users.models import User

__all__ = ("user_auth",)


class OAuth2PasswordBearerJSON(HTTPBearer):
    header_name = "Authorization"
    schema = settings.AUTHENTICATION.scheme

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        authorization = request.headers.get(self.header_name)
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise HTTPException(
                    code="INVALID_AUTHENTICATION",
                    status_code=status.HTTP_403_FORBIDDEN,
                    message="Not authenticated",
                )
            else:
                return None
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    code="INVALID_AUTHENTICATION",
                    status_code=status.HTTP_403_FORBIDDEN,
                    message="Invalid authentication credentials",
                )
            else:
                return None
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)


oauth2_scheme = OAuth2PasswordBearerJSON()


class UserAuth:
    SECRET_KEY = settings.AUTHENTICATION.access_token.secret_key
    ALGORITHM = settings.AUTHENTICATION.algorithm

    @classmethod
    def create_access_token(cls, data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()  # copy data for encoding
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})  # current live time
        encoded_jwt = jwt.encode(
            payload=to_encode, key=cls.SECRET_KEY, algorithm=cls.ALGORITHM
        )
        return encoded_jwt

    @classmethod
    def decode_token(cls, token: str) -> dict:
        return jwt.decode(jwt=token, key=cls.SECRET_KEY, algorithms=cls.ALGORITHM)

    @classmethod
    async def validate_user(cls, username: str, password: str) -> User | None:
        user: User | None = await aauthenticate(username=username, password=password)
        if user is None:
            raise HTTPException(
                message="Invalid credentials",
                status_code=status.HTTP_400_BAD_REQUEST,
                code="INVALID_CREDENTIALS",
            )
        if user.is_active is True:
            return user
        return None

    @classmethod
    async def get_current_user(
        cls, model: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)]
    ) -> User:
        # Exception for invalid credentials
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Could not validate credentials",
            code="INVALID_CREDENTIALS",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            # Decode token
            payload = cls.decode_token(model.credentials)
            # Data from token
            user_id: str = str(payload.get("id"))
            username: str = str(payload.get("username"))
            exp: str = str(payload.get("exp"))
            if username is None:
                raise credentials_exception
            # If token is expired
            if datetime.fromtimestamp(float(exp), tz=timezone.utc) < datetime.now(
                timezone.utc
            ):
                raise credentials_exception

        except InvalidTokenError:
            raise credentials_exception

        # Check user
        user: User | None = await User.objects.filter(
            id=user_id, username=username, is_active=True
        ).afirst()

        if user is None:
            raise credentials_exception
        return user

    async def login_for_access_token(
        self, username: str, password: str
    ) -> TokenSchemaResponse:
        user: User | None = await self.validate_user(
            username, password
        )  # Validate user
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Incorrect username or password",
                code="INVALID_CREDENTIALS",
                headers={"WWW-Authenticate": oauth2_scheme.schema},
            )

        access_token_expires = timedelta(
            seconds=settings.AUTHENTICATION.access_token.ttl
        )  # Delta lifetime
        # Data for decoding
        access_token = self.create_access_token(
            data={
                "id": str(user.id),  # UUID
                "email": user.email,
                "username": user.username,
            },
            expires_delta=access_token_expires,
        )  # Create access token

        return TokenSchemaResponse(
            access_token=access_token,
            token_type=oauth2_scheme.schema,
            access_token_expires=access_token_expires.total_seconds(),
        )

    @staticmethod
    def block_endpoint(request: Request):
        if request.headers.get(oauth2_scheme.header_name):
            raise HTTPException(
                code="INVALID_AUTHENTICATION",
                status_code=status.HTTP_403_FORBIDDEN,
                message="Already authenticated",
            )


user_auth = UserAuth()
