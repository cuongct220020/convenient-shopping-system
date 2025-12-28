from sqlalchemy import Integer, JSON, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base


class GroupPreference(Base):
    __tablename__ = "group_preferences"

    group_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_tag_list: Mapped[list[int]] = mapped_column(JSON, nullable=False)


class TagRelation(Base):
    __tablename__ = "tag_relations"

    user_tag: Mapped[int] = mapped_column(Integer, primary_key=True)
    ingredient_tag: Mapped[int] = mapped_column(Integer, primary_key=True)
    relation: Mapped[bool] = mapped_column(Boolean, nullable=False)

