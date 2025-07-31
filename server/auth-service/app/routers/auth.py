"""
This module contains the router for the health API.
"""
from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.logger import logger
from app.schemas.signup import SignupSchema
from app.schemas.signin import SigninSchema
from app.services.user_service import UserService

router = APIRouter()
# user_service = UserService()


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_description="Signup API",
    tags=["Auth"],
    operation_id="auth_signup_v1"
)
async def auth_signup_handler(
    signup_data: SignupSchema,
    user_service: UserService = Depends()
):
    """
    User signup endpoint to register a new user.
    """
    await user_service.create_user(signup_data)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "User created successfully",
            "data": signup_data.model_dump(exclude={"password"}),
        }
    )


@router.post(
    "/signin",
    status_code=status.HTTP_200_OK,
    response_description="Signin API",
    tags=["Auth"],
    operation_id="auth_signin_v1"
)
async def auth_signin_handler(
    signin_data: SigninSchema,
    user_service: UserService = Depends()
):
    """
    User signin endpoint to register a new user.
    """
    result = await user_service.authenticate_user(signin_data)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=result
    )


@router.put("/verify/email", operation_id="auth_verify_email_v1")
async def auth_verify_email_handler(
    user_service: UserService = Depends()
):
    """
    User verify email endpoint to verify user email.
    """
    await user_service.verify_email(data)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Email verified"}
    )


@router.put("/forgot/password", operation_id="auth_forgot_password_v1")
async def auth_forgot_password_handler(user_service: UserService = Depends()):
    """
    Forgot password endpoint to verify reset password.
    """
    await user_service.send_password_reset_link(data.email)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Reset link sent"}
    )


@router.put("/reset/password/{token}", operation_id="auth_reset_password_v1")
async def auth_reset_password_handler(token: str, user_service: UserService = Depends()):
    """
    Reset password endpoint to verify reset password token.
    """
    await user_service.reset_password(token, data.new_password)
    return JSONResponse(
        status_code=200,
        content={"message": "Password has been reset"}
    )


@router.put("/change/password", operation_id="auth_change_password_v1")
async def auth_change_password_handler(user_service: UserService = Depends()):
    """
    Change password endpoint to verify change password.
    """
    await user_service.change_password(data)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Password changed"}
    )


@router.get("/currentuser", operation_id="auth_current_user_v1")
async def auth_current_user_handler(user_service: UserService = Depends()):
    """
    Get the current authenticated user.
    """
    user = await user_service.get_current_user()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"user": user}
    )


@router.post("/resend/email", operation_id="auth_resend_email_v1")
async def auth_resend_email_handler(user_service: UserService = Depends()):
    """
    Resend verification email endpoint to resend verification email."""
    await user_service.resend_verification_email(data.email)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Verification email resent"}
    )
