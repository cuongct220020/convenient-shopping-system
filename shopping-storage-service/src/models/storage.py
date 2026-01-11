import uuid
from sqlalchemy import Integer, String, Float, Enum, ForeignKey, CheckConstraint, Date, event, update
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import date
from typing import Optional
from enums.uc_measurement_unit import UCMeasurementUnit
from enums.storage_type import StorageType
from core.database import Base

class Storage(Base):
    __tablename__ = "storages"

    storage_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    storage_name: Mapped[str] = mapped_column(String, nullable=True)
    storage_type: Mapped[StorageType] = mapped_column(Enum(StorageType), nullable=False)
    group_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    storage_unit_list: Mapped[list["StorableUnit"]] = relationship(
        back_populates="storage",
        cascade="all, delete-orphan"
    )

@event.listens_for(Storage, "after_insert")
def set_storage_name_after_insert(mapper, connection, target):
    if not target.storage_name:
        new_name = f"{target.storage_type.name.replace('_', ' ').title()} #{target.storage_id} of Group #{target.group_id}"
        connection.execute(
            update(Storage)
            .where(Storage.storage_id == target.storage_id)
            .values(storage_name=new_name)
        )
        target.storage_name = new_name

class StorableUnit(Base):
    __tablename__ = "storable_units"

    unit_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    storage_id: Mapped[int] = mapped_column(ForeignKey("storages.storage_id"), nullable=False)
    package_quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_name: Mapped[str] = mapped_column(String, nullable=False)
    component_id: Mapped[Optional[int]] = mapped_column(Integer)
    content_type: Mapped[Optional[str]] = mapped_column(String)
    content_quantity: Mapped[Optional[float]] = mapped_column(Float)
    content_unit: Mapped[Optional[UCMeasurementUnit]] = mapped_column(Enum(UCMeasurementUnit))
    added_date: Mapped[date] = mapped_column(Date, server_default=func.current_date(), nullable=False)
    expiration_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    storage: Mapped["Storage"] = relationship(
        back_populates="storage_unit_list",
        foreign_keys=[storage_id]
    )

    __table_args__ = (
        CheckConstraint(
            "(component_id IS NULL AND content_type IS NULL) "
            "OR (component_id IS NOT NULL AND content_type IS NOT NULL)",
            name="component_id_type_pairing"
        ),
        CheckConstraint(
            "(content_type = 'countable_ingredient' AND "
            " content_quantity IS NULL AND content_unit IS NULL) "
            "OR "
            "(content_type = 'uncountable_ingredient' AND "
            " content_quantity IS NOT NULL AND content_unit IS NOT NULL)",
            name="quantity_unit_required_for_measurable"
        )
    )