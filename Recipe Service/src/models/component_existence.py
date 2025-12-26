from sqlalchemy import Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base


class ComponentExistence(Base):
    __tablename__ = "component_existence"

    group_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    component_name_list: Mapped[list[str]] = mapped_column(JSON, nullable=False)

