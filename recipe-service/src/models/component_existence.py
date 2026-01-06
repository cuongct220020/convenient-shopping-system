import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base


class ComponentExistence(Base):
    __tablename__ = "component_existence"

    group_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    component_name_list: Mapped[list[str]] = mapped_column(JSONB, nullable=False)

