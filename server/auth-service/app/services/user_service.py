"""
This module contains the user service for handling user-related operations.
"""
import uuid
from uuid import UUID
from typing import Dict, List
from datetime import datetime, timedelta
import random


from fastapi import Depends

from app.repositories.user_repository import UserRepository
from app.schemas.signup import SignupSchema, UpdateUserSchema, UserOutSchema
from app.schemas.signin import SigninSchema
from app.schemas.password import EmailSchema, PasswordSchema, ChangePasswordSchema
from app.models.user import User
from app.core.exceptions import UserAlreadyExists, UserNotFound, InvalidCredentials, InvalidToken
from app.utils.security import (
    generate_password_hash,
    create_url_safe_token,
    decode_url_safe_token,
    create_access_token,
    verify_password
)
from app.services.rabbitmq.connection import create_rabbitmq_channel
from app.services.rabbitmq.producer import publish_message_to_queue
from app.core.config import config
from app.core.logger import logger

from server_shared.cloudinary_upload import CloudinaryUploader
from server_shared.utils.helpers.string_utils import StringUtils


class UserService:
    """
    This service handles user-related operations such as creating, updating, retrieving, and deleting users.
    It interacts with the UserRepository to perform database operations.
    """

    def __init__(self, user_repo: UserRepository = Depends()):
        self.user_repo = user_repo
        self.rabbitmq_configuration = {
            "msa_email_queue": {
                "exchange_name": "msa-email-notification",
                "routing_key": "auth-email"
            },
            "msa_buyer_update_queue": {
                "exchange_name": "msa-buyer-update",
                "routing_key": "user-buyer",
            }
        }
        self.__cloudinary_service = CloudinaryUploader(
            cloud_name=config.CLOUDINARY_CLOUD_NAME,
            api_key=config.CLOUDINARY_API_KEY,
            api_secret=config.CLOUDINARY_API_SECRET
        )

    async def create_user(self, signup_data: SignupSchema) -> Dict:
        """
        Create a new user in the database.
        """
        existing = await self.user_repo.get_by_email_or_username(signup_data.email, signup_data.username)
        if existing:
            raise UserAlreadyExists("User already exists")
        profile_public_id = str(uuid.uuid4())
        # TODO: Add code to upload image
        hashed_password = generate_password_hash(signup_data.password)
        signup_data.password = hashed_password
        user = User(**signup_data.model_dump(),
                    profile_public_id=profile_public_id)
        created_user = await self.user_repo.create(user)
        verification_token = create_url_safe_token(
            {"email": signup_data.email})
        # Publish a message to the RabbitMQ queue for buyer creation
        auth_channel = await create_rabbitmq_channel()
        await publish_message_to_queue(
            channel=auth_channel,
            exchange_name=self.rabbitmq_configuration["msa_buyer_update_queue"]["exchange_name"],
            routing_key=self.rabbitmq_configuration["msa_buyer_update_queue"]["routing_key"],
            message={
                "user_data": {
                    "username": created_user.username,
                    "email": created_user.email,
                    "profile_picture": created_user.profile_picture,
                    "country": created_user.country
                },
                "from": "auth_service"
            }
        )
        # Publish a message to the RabbitMQ queue for user notification
        await publish_message_to_queue(
            channel=auth_channel,
            exchange_name=self.rabbitmq_configuration["msa_email_queue"]["exchange_name"],
            routing_key=self.rabbitmq_configuration["msa_email_queue"]["routing_key"],
            message={
                "template": "verifyEmail",
                "receiverEmail": created_user.email,
                "username": created_user.username,
                "verifyLink": f"{config.CLIENT_URL}/verify/email?token={verification_token}",
                "resetLink": ""
            }
        )
        # TODO: Any other publish to queue will appear here

        jwt_token = create_access_token(
            {
                "id": str(created_user.uuid),
                "email": created_user.email,
                "username": created_user.username,
            }
        )
        return {
            "user": created_user.model_dump(mode="json"),
            "token": jwt_token,
        }

    async def authenticate_user(self, signin_data: SigninSchema) -> Dict:
        """
        Authenticate a user with email or username and password.
        """
        is_email = StringUtils.is_email(signin_data.username)

        # Retrieve user by email or username
        user = await self.user_repo.get_by_email(signin_data.username) if is_email \
            else await self.user_repo.get_by_username(signin_data.username)

        if not user:
            raise UserNotFound("User not found")

        if not verify_password(signin_data.password, user.password):
            raise InvalidCredentials("Invalid Credentials")

        user_modal = UserOutSchema.model_validate(user)
        serialized_user = user_modal.model_dump(mode="json")

        response = {
            "user": serialized_user,
            "is_verified": user.is_verified,
            "token": "",
            "browserName": "",
            "deviceType": ""
        }

        if (
            signin_data.browserName != user.browser_name or
            signin_data.deviceType != user.device_type
        ):
            otp_code = str(random.randint(100000, 999999))
            expiry = datetime.utcnow() + timedelta(minutes=10)
            user.otp = otp_code
            user.otp_expiration = expiry
            user.browser_name = signin_data.browserName
            user.device_type = signin_data.deviceType

            await self.user_repo.update(user)
            auth_channel = await create_rabbitmq_channel()
            await publish_message_to_queue(
                channel=auth_channel,
                exchange_name=self.rabbitmq_configuration["msa_email_queue"]["exchange_name"],
                routing_key=self.rabbitmq_configuration["msa_email_queue"]["routing_key"],
                message={
                    "template": "otpEmail",
                    "receiverEmail": user.email,
                    "username": user.username,
                    "otp": otp_code
                }
            )

            response["message"] = "OTP code sent"
            response["browserName"] = user.browser_name
            response["deviceType"] = user.device_type
        else:
            jwt_token = create_access_token(
                {
                    "id": str(user.uuid),
                    "email": user.email,
                    "username": user.username,
                }
            )
            response["token"] = jwt_token
        return response

    async def get_user_by_id(self, user_id: UUID) -> Dict:
        """
        Get a user by id from the database.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound()
        user_modal = UserOutSchema.model_validate(user)
        serialized_user = user_modal.model_dump(mode="json")
        return serialized_user

    async def update_user(self, user_id: UUID, data: UpdateUserSchema) -> User:
        """
        Update a user in the database.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound("User not found")

        for field, value in data.dict(exclude_unset=True).items():
            setattr(user, field, value)

        return await self.user_repo.update(user)

    async def delete_user(self, user_id: UUID) -> bool:
        """
        delete a user from the database.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound("User not found")
        await self.user_repo.delete(user)
        return True

    async def list_users(self, limit: int = 10, offset: int = 0) -> List[dict]:
        """
        List users with pagination and return serialized output.
        """
        users = await self.user_repo.list_users(limit, offset)

        # Convert ORM objects to Pydantic models
        user_models = [UserOutSchema.model_validate(user) for user in users]

        # Serialize Pydantic models into JSON-compatible dictionaries
        serialized_users = [user.model_dump(
            mode="json") for user in user_models]

        return serialized_users

    async def send_verification_email(self, email_data: EmailSchema):
        """
        Send user a password reset link with token.
        """
        existing = await self.user_repo.get_by_email(email_data.email)
        if not existing:
            raise UserNotFound("User not found")
        verification_token = create_url_safe_token({
            "email": email_data.email
        })
        # Publish a message to the RabbitMQ queue for email notification
        await publish_message_to_queue(
            channel=auth_channel,
            exchange_name=self.rabbitmq_configuration["msa_email_queue"]["exchange_name"],
            routing_key=self.rabbitmq_configuration["msa_email_queue"]["routing_key"],
            message={
                "template": "verifyEmail",
                "receiverEmail": existing.email,
                "username": existing.username,
                "verifyLink": f"{config.CLIENT_URL}/verify/email?token={verification_token}",
                "resetLink": ""
            }
        )

    async def verify_user_email(self, token: str):
        """
        Verify user email with token.
        """
        user_data = decode_url_safe_token(token)
        if not user_data:
            raise InvalidToken("Token not valid")
        logger.info(f"user_data: {user_data}")

        email = user_data.get("email")
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise UserNotFound("User not found")
        user.is_verified = True
        await self.user_repo.update(user)

    async def send_password_reset_link(self, email_data: EmailSchema):
        """
        Send user a password reset link with token.
        """
        existing = await self.user_repo.get_by_email(email_data.email)
        if not existing:
            raise UserNotFound("User not found")
        verification_token = create_url_safe_token({
            "email": email_data.email
        })
        # Publish a message to the RabbitMQ queue for email notification
        auth_channel = await create_rabbitmq_channel()
        await publish_message_to_queue(
            channel=auth_channel,
            exchange_name=self.rabbitmq_configuration["msa_email_queue"]["exchange_name"],
            routing_key=self.rabbitmq_configuration["msa_email_queue"]["routing_key"],
            message={
                "template": "forgotPassword",
                "receiverEmail": existing.email,
                "username": existing.username,
                "resetLink": f"{config.CLIENT_URL}/reset/password?token={verification_token}",
            }
        )

    async def reset_password(self, token: str, password_data: PasswordSchema):
        """
        Reset password API.
        """
        user_data = decode_url_safe_token(token)
        if not user_data:
            raise InvalidToken("Token not valid")
        logger.info(f"user_data: {user_data}")

        email = user_data.get("email")
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise UserNotFound("User not found")

        user.password = generate_password_hash(password_data.password)
        await self.user_repo.update(user)

        # Publish a message to the RabbitMQ queue for email notification
        auth_channel = await create_rabbitmq_channel()
        await publish_message_to_queue(
            channel=auth_channel,
            exchange_name=self.rabbitmq_configuration["msa_email_queue"]["exchange_name"],
            routing_key=self.rabbitmq_configuration["msa_email_queue"]["routing_key"],
            message={
                "template": "resetPasswordSuccess",
                "receiverEmail": user.email,
                "username": user.username
            }
        )

    async def change_password(self, email: str, change_password_data: ChangePasswordSchema):
        """
        Change password API.
        """
        # Fetch the user from DB
        existing_user = await self.user_repo.get_by_email(email)
        if not existing_user:
            raise UserNotFound("User not found")

        old_password_hash = generate_password_hash(
            change_password_data.current_password)
        if not verify_password(change_password_data.current_password, old_password_hash):
            raise InvalidCredentials("Invalid Credentials")

        # Hash the new password
        hashed_password = generate_password_hash(
            change_password_data.new_password)

        # Update in database
        existing_user.password = hashed_password
        await self.user_repo.update(existing_user)

        # Publish message to RabbitMQ
        auth_channel = await create_rabbitmq_channel()
        await publish_message_to_queue(
            channel=auth_channel,
            exchange_name=self.rabbitmq_configuration["msa_email_queue"]["exchange_name"],
            routing_key=self.rabbitmq_configuration["msa_email_queue"]["routing_key"],
            message={
                "template": "resetPasswordSuccess",
                "receiverEmail": existing_user.email,
                "username": existing_user.username
            }
        )
