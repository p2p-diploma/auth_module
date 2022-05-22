from http.client import HTTPException
from typing import Any, Optional

from pydantic import BaseModel
from starlette import status


class APIException(HTTPException):
    class Schema(BaseModel):
        code: str
        detail: str

    default_status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_code: str = "internal_error"
    default_detail: str = "Internal Error."

    def __init__(
        self,
        status_code: Optional[int] = None,
        detail: Optional[str] = None,
        headers: Optional[dict[str, Any]] = None,
    ):
        if status_code is None:
            status_code = self.default_status_code
        if detail is None:
            detail = self.default_detail
        super().__init__(status_code, detail, headers)


class InvalidLoginData(APIException):
    default_status_code = status.HTTP_400_BAD_REQUEST
    default_code = "invalid_data"
    default_detail = "Not valid login data"


class UserIsBanned(APIException):
    default_status_code = status.HTTP_403_FORBIDDEN
    default_code = "user_is_banned"
    default_detail = "You are banned"


class NotFoundException(APIException):
    default_status_code = status.HTTP_404_NOT_FOUND
    default_code = "not_found"
    default_detail = "Not found"


class KudaPoperError(APIException):
    default_status_code = status.HTTP_403_FORBIDDEN
    default_code = "access_denied"
    default_detail = "Access denied"


class InvalidRefreshToken(APIException):
    default_status_code = status.HTTP_403_FORBIDDEN
    default_code = "invalid_refresh_token"
    default_detail = "Your refresh token is invalid"


class NoPermissionToDo(APIException):
    default_status_code = status.HTTP_400_BAD_REQUEST
    default_code = "not_enough_privileges"
    default_detail = "You don't have privileges to do this"


class SameEmailError(APIException):
    default_status_code = status.HTTP_400_BAD_REQUEST
    default_code = "same_user_email"
    default_detail = "The user with this email already exists in the system."


class SomethingWentWrongException(APIException):
    default_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_code = "something_went_wrong"
    default_detail = "Sorry. Something Went Wrong. Please, contact us!"
