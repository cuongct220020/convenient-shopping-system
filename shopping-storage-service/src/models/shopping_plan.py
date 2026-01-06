import uuid
from sqlalchemy import Integer, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from enums.plan_status import PlanStatus
from core.database import Base

class ShoppingPlan(Base):
    __tablename__ = "shopping_plans"

    plan_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    last_modified: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    assigner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    assignee_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    shopping_list: Mapped[list] = mapped_column(JSONB, nullable=False)
    others: Mapped[list] = mapped_column(JSONB, nullable=True)
    plan_status: Mapped[PlanStatus] = mapped_column(Enum(PlanStatus), nullable=False, default=PlanStatus.CREATED)

    report: Mapped["Report"] = relationship(back_populates="plan")

class Report(Base):
    __tablename__ = "reports"

    report_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("shopping_plans.plan_id"), nullable=False, unique=True)
    report_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    report_content: Mapped[list] = mapped_column(JSONB, nullable=False)
    spent_amount: Mapped[int] = mapped_column(Integer, default=0)

    plan: Mapped["ShoppingPlan"] = relationship(
        back_populates="report",
        foreign_keys=[plan_id],
        single_parent=True
    )