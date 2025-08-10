"""
Database manager for user model
"""
from typing import Optional, List
from uuid import UUID

from fastapi import Depends
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.database import get_db_session
class UserRepository:
    """
    Repository for handling authentication-related database operations.
    This class interacts with the Auth model to perform CRUD operations."""
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Get a user by id from the database.
        :param user_id: ID of the user to retrieve.
        :return: User object if found, None otherwise.
        """
        statement = select(User).where(User.uuid == user_id)
        result = await self.session.exec(statement) # type: ignore
        return result.first()


    async def get_by_email_or_username(self, email: str, username: str) -> Optional[User]:
        """
        Get a user by email or username from the database.
        :param email: Email of the user to retrieve.
        :param username: Username of the user to retrieve.
        :return: User object if found, None otherwise.
        """
        result = await self.session.exec( # type: ignore
            select(User).where(
                (User.email == email) | (User.username == username)
            )
        )
        return result.first()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by email or username from the database.
        :param email: Email of the user to retrieve.
        :param username: Username of the user to retrieve.
        :return: User object if found, None otherwise.
        """
        result = await self.session.exec( # type: ignore
            select(User).where(
                (User.username == username)
            )
        )
        return result.first()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email or username from the database.
        :param email: Email of the user to retrieve.
        :param username: Username of the user to retrieve.
        :return: User object if found, None otherwise.
        """
        result = await self.session.exec( # type: ignore
            select(User).where(
                (User.email == email)
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

    async def list_users(self, limit: int = 10, offset: int = 0) -> List[User]:
        """
        List users with pagination.
        :param limit: Number of users to return.
        :param offset: Number of users to skip.
        :return: List of User objects.
        """
        result = await self.session.exec( # type: ignore
            select(User).offset(offset).limit(limit)
        )
        users = result.all()
        return users
