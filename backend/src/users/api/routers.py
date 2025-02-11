from asgiref.sync import sync_to_async
from django.db.utils import IntegrityError
from fastapi import APIRouter, Depends, status

from core.schemas import HTTPException, MessageResponse, Response
from users.api.auth.security import user_auth
from users.api.schemas import (
    BaseUserResponseSchema,
    TokenSchemaResponse,
    UserResponseSchema,
    UserSingInSchema,
    UserSingUpSchema,
)
from users.models import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    path="/sign-up/",
    response_model=Response[MessageResponse[BaseUserResponseSchema]],
    status_code=status.HTTP_201_CREATED,
)
async def sign_up(body: UserSingUpSchema):
    try:
        obj = await sync_to_async(User.objects.create_user, thread_sensitive=True)(
            body.username, body.password, email=body.email
        )
        message = MessageResponse[BaseUserResponseSchema](
            message="User already created",
            code="USER_ALREADY_CREATED",
            detail=BaseUserResponseSchema(id=obj.id),
        )
        return Response[MessageResponse[BaseUserResponseSchema]](data=message)
    except IntegrityError as e:
        if "unique constraint" in str(e):
            raise HTTPException(
                message="The username already exists",
                status_code=400,
                code="USER_EXISTS",
            )


@router.post(
    path="/sign-in/",
    response_model=Response[TokenSchemaResponse],
    dependencies=[Depends(user_auth.block_endpoint)],
)
async def sign_in(body: UserSingInSchema):
    token = await user_auth.login_for_access_token(body.username, body.password)
    return Response[TokenSchemaResponse](data=token)


@router.get(path="/profile/", response_model=Response[UserResponseSchema])
async def get_account(user: User = Depends(user_auth.get_current_user)):
    return Response[UserResponseSchema](data=UserResponseSchema.model_validate(user))
