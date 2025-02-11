from fastapi import status

from core.schemas import HTTPException


class NotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            message="Not found",
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
        )


class BadRequest(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            message="Bad request",
            status_code=status.HTTP_400_BAD_REQUEST,
            code="BAD_REQUEST",
        )


class Forbidden(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            message="Forbidden",
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN",
        )


class UnhandledError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            message="Unhandled error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="INTERNAL_SERVER_ERROR",
        )
