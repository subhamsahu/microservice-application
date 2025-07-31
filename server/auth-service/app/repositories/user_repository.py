from typing import Optional

from fastapi import Depends
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.database import get_db_session
from app.core.logger import logger


class UserRepository:
    """
    Repository for handling authentication-related database operations.
    This class interacts with the Auth model to perform CRUD operations."""
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by id from the database.
        :param user_id: ID of the user to retrieve.
        :return: User object if found, None otherwise.
        """
        return await self.session.get(User, user_id)

    async def get_by_email_or_username(self, email: str, username: str) -> Optional[User]:
        """
        Get a user by email or username from the database.
        :param email: Email of the user to retrieve.
        :param username: Username of the user to retrieve.
        :return: User object if found, None otherwise.
        """
        result = await self.session.exec(
            select(User).where(
                (User.email == email) | (User.username == username)
            )
        )
        return result.first()

    async def create(self, user: User) -> User:
        """
        Create a user in the database.
        :param user: User object with updated data.
        :return: Updated User object.
        """
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: User) -> User:
        """
        Update a user in the database.
        :param user: User object with updated data.
        :return: Updated User object.
        """
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User):
        """
        Delete a user from the database.
        :param user: User object to delete.
        :return: None
        """
        await self.session.delete(user)
        await self.session.commit()
