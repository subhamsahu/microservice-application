import logging
from typing import Any, Dict, List, Optional

from sqlmodel import select
from sqlalchemy import MetaData, Table, insert, update as sql_update, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.exc import NoResultFound
from sqlmodel.ext.asyncio.session import AsyncSession

from ..utils.abstract_classes import AbstractAsyncDatabaseManager, AbstractAsyncDatabaseConnection

logger = logging.getLogger(__name__)


class SQLModelAsyncDatabaseManager(AbstractAsyncDatabaseManager):
    """
    Generic async database manager using SQLModel and dynamic table reflection.
    Provides CRUD operations on a specified table.
    """

    def __init__(self, db_connection: AbstractAsyncDatabaseConnection, table_name: str):
        super().__init__(db_connection)
        self.db_connection = db_connection
        self.table_name = table_name
        self.engine: Optional[AsyncEngine] = db_connection.get_engine()
        self.table: Optional[Table] = None

    async def _get_table(self) -> Table:
        """
        Reflect and return SQLAlchemy Table object for the given table name.
        """
        if self.table is None:
            if not self.engine:
                self.engine = await self.db_connection.connect()

            metadata = MetaData()
            try:
                self.table = Table(self.table_name, metadata, autoload_with=self.engine)
                logger.info(f"✅ Reflected table '{self.table_name}' successfully.")
            except Exception as e:
                logger.error(f"❌ Failed to reflect table '{self.table_name}': {e}")
                raise RuntimeError(f"Could not reflect table '{self.table_name}': {e}")
        return self.table

    async def create(self, data: Dict[str, Any]) -> int:
        """
        Creates a new record in the database.
        Returns the inserted record ID.
        """
        table = await self._get_table()
        async with self.db_connection.get_session() as session:
            stmt = insert(table).values(**data)
            result = await session.execute(stmt)
            await session.commit()
            inserted_id = result.inserted_primary_key[0]
            logger.info(f"✅ Inserted record into '{self.table_name}' with ID: {inserted_id}")
            return inserted_id

    async def read(self, record_id: Any) -> Dict[str, Any]:
        """
        Reads a record by ID.
        """
        table = await self._get_table()
        async with self.db_connection.get_session() as session:
            stmt = select(table).where(table.c.id == record_id)
            result = await session.execute(stmt)
            row = result.first()
            if row is None:
                logger.warning(f"⚠️ Record with ID {record_id} not found in '{self.table_name}'")
                raise KeyError(f"Record with ID {record_id} not found")
            return dict(row._mapping)

    async def update(self, record_id: Any, data: Dict[str, Any]) -> None:
        """
        Updates a record by ID.
        """
        table = await self._get_table()
        async with self.db_connection.get_session() as session:
            stmt = sql_update(table).where(table.c.id == record_id).values(**data)
            result = await session.execute(stmt)
            if result.rowcount == 0:
                logger.warning(f"⚠️ No record updated with ID {record_id} in '{self.table_name}'")
                raise KeyError(f"Record with ID {record_id} not found")
            await session.commit()
            logger.info(f"✅ Updated record with ID {record_id} in '{self.table_name}'")

    async def delete(self, record_id: Any) -> None:
        """
        Deletes a record by ID.
        """
        table = await self._get_table()
        async with self.db_connection.get_session() as session:
            stmt = sql_delete(table).where(table.c.id == record_id)
            result = await session.execute(stmt)
            if result.rowcount == 0:
                logger.warning(f"⚠️ No record deleted with ID {record_id} in '{self.table_name}'")
                raise KeyError(f"Record with ID {record_id} not found")
            await session.commit()
            logger.info(f"🗑️ Deleted record with ID {record_id} from '{self.table_name}'")

    async def list(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Lists all records in the table, optionally paginated.
        """
        table = await self._get_table()
        async with self.db_connection.get_session() as session:
            stmt = select(table).limit(limit).offset(offset)
            result = await session.execute(stmt)
            rows = result.fetchall()
            logger.info(f"📋 Listed {len(rows)} records from '{self.table_name}'")
            return [dict(row._mapping) for row in rows]
