# shopping_shared/databases/base_repository.py
from typing import Any, Generic, Optional, Sequence, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect

ModelType = TypeVar("ModelType", bound=Any)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    A generic repository class providing basic asynchronous CRUD operations.

    This class is framework-agnostic and relies only on SQLAlchemy's AsyncSession
    and Pydantic models.

    :param model: The SQLAlchemy model class.
    :param session: The SQLAlchemy AsyncSession to be used for database operations.
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
        # Get the name of the primary key column for the model
        self._pk_name = inspect(self.model).primary_key[0].name

    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        """
        Fetches a single record by its primary key.

        :param id: The primary key of the record to fetch.
        :return: The model instance or None if not found.
        """
        return await self.session.get(self.model, id)

    async def get_all(
        self, *, offset: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        """
        Fetches multiple records with optional pagination.

        :param offset: The number of records to skip.
        :param limit: The maximum number of records to return.
        :return: A sequence of model instances.
        """
        stmt = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """
        Creates a new record in the database.
        Note: This is a simplified create method and does not handle nested relationships.
        For complex creations, this method should be overridden in the specific repository.

        :param obj_in: A Pydantic schema instance with the data for the new record.
        :return: The newly created model instance.
        """
        # model_dump is equivalent to dict() but more configurable
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        self.session.add(db_obj)
        await self.session.flush()  # Use flush to get the DB-generated values like IDs
        await self.session.refresh(db_obj)
        return db_obj

    async def update(
        self, id: Any, obj_in: UpdateSchemaType
    ) -> Optional[ModelType]:
        """
        Updates an existing record in the database.

        :param id: The primary key of the record to update.
        :param obj_in: A Pydantic schema instance with the fields to update.
        :return: The updated model instance or None if the record was not found.
        """
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return None

        # Use exclude_unset=True to only update fields that were provided
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: Any) -> Optional[ModelType]:
        """
        Deletes a record from the database.

        :param id: The primary key of the record to delete.
        :return: The deleted model instance or None if the record was not found.
        """
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return None
        await self.session.delete(db_obj)
        await self.session.flush()
        return db_obj
