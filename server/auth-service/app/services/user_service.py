"""
This module contains the user service for handling user-related operations.
"""
from fastapi import Depends
from app.repositories.user_repository import UserRepository
from app.schemas.signup import SignupSchema, UpdateUserSchema
from app.models.user import User
from app.core.exceptions import UserAlreadyExists, UserNotFound
from app.utils.security import generate_password_hash
from app.services.rabbitmq.connection import auth_channel
from app.services.rabbitmq.producer import publish_message_to_queue


class UserService:
    """
    This service handles user-related operations such as creating, updating, retrieving, and deleting users.
    It interacts with the UserRepository to perform database operations.
    """

    def __init__(self, user_repo: UserRepository = Depends()):
        self.user_repo = user_repo
        self.rabbitmq_configuration = {
            "exchange_name": "msa-email-notification",
            "routing_key": "auth-email",
        }

    async def create_user(self, signup_data: SignupSchema) -> User:
        """
        Create a new user in the database.
        """
        existing = await self.user_repo.get_by_email_or_username(signup_data.email, signup_data.username)
        if existing:
            raise UserAlreadyExists("User already exists")
        hashed_password = generate_password_hash(signup_data.password)
        signup_data.password = hashed_password
        user = User(**signup_data.model_dump())
        created_user = await self.user_repo.create(user)
        verification_token = "xxxxx"
        # Publish a message to the RabbitMQ queue for email notification
        await publish_message_to_queue(
            channel=auth_channel,
            exchange_name=self.rabbitmq_configuration["exchange_name"],
            routing_key=self.rabbitmq_configuration["routing_key"],
            message={
                "template": "verifyEmail",
                "receiverEmail": created_user.email,
                "username": created_user.username,
                "verifyLink": f"http://localhost:3000/verify?token={verification_token}",
                "resetLink": ""
            }
        )
        return created_user

    async def get_user_by_id(self, user_id: int) -> User:
        """
        Get a user by id from the database.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound()
        return user

    async def update_user(self, user_id: int, data: UpdateUserSchema) -> User:
        """
        Update a user in the database.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound("User not found")

        for field, value in data.dict(exclude_unset=True).items():
            setattr(user, field, value)

        return await self.user_repo.update(user)

    async def delete_user(self, user_id: int):
        """
        delete a user from the database.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound("User not found")

        await self.user_repo.delete(user)
        return {"message": "User deleted"}
