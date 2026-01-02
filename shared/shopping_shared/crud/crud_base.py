from typing import Generic, TypeVar, Optional, Sequence, Dict, Any
from sqlalchemy.orm import Session, DeclarativeBase
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.inspection import inspect
from pydantic import BaseModel
from fastapi import HTTPException

"""
    Generic CRUD base class for reuse across CRUD operations of different models
"""

ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        self.model = model
        self._relationships = {name: rel for name, rel in inspect(self.model).relationships.items()}

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        return db.get(self.model, id)

    def get_many(self, db: Session, cursor: Optional[int] = None, limit: int = 100) -> Sequence[ModelType]:
        pk = inspect(self.model).primary_key[0]
        stmt = select(self.model).order_by(pk.desc()).limit(limit)
        if cursor is not None:
            stmt = stmt.where(pk < cursor)
        return db.execute(stmt).scalars().all()

    def delete(self, db: Session, id: int) -> ModelType:
        obj = db.get(self.model, id)
        db.delete(obj)
        db.commit()
        return obj

    def _separate_data(self, obj_data: Dict[str, Any]):
        scalar_data = {}
        relationship_data = {}
        for key, value in obj_data.items():
            if key in self._relationships:
                relationship_data[key] = value
            else:
                scalar_data[key] = value
        return scalar_data, relationship_data

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.model_dump()
        scalar_data, relationship_data = self._separate_data(obj_in_data)
        db_obj = self.model(**scalar_data)
        for field, value in relationship_data.items():
            if value is not None:
                related_model = self._relationships[field].mapper.class_
                related_objects = [related_model(**item) for item in value]
                setattr(db_obj, field, related_objects)
        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Integrity error: {str(e)}")
        return db_obj

    def update(self, db: Session, obj_in: UpdateSchemaType, db_obj: ModelType) -> ModelType:
        obj_in_data = obj_in.model_dump(exclude_unset=True)
        scalar_data, relationship_data = self._separate_data(obj_in_data)
        for field, value in scalar_data.items():
            setattr(db_obj, field, value)
        for field, value in relationship_data.items():
            if value is not None:
                related_model = self._relationships[field].mapper.class_
                new_objects = [related_model(**item) for item in value]
                setattr(db_obj, field, new_objects)
        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Integrity error: {str(e)}")
        return db_obj




