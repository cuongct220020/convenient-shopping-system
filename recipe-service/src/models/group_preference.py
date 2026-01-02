from sqlalchemy import Integer, String, Boolean, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base


class GroupPreference(Base):
    __tablename__ = "group_preferences"

    group_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_tag_list: Mapped[list[str]] = mapped_column(JSONB, nullable=False)


class TagRelation(Base):
    __tablename__ = "tag_relations"

    user_tag: Mapped[str] = mapped_column(String)
    user_tag_name: Mapped[str] = mapped_column(String, nullable=False)
    ingredient_tag: Mapped[str] = mapped_column(String)
    ingredient_tag_name: Mapped[str] = mapped_column(String, nullable=False)
    relation: Mapped[bool] = mapped_column(Boolean, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("user_tag", "ingredient_tag"),
    )

