"""
UsageLog model for billing and usage tracking.
"""

import uuid
from typing import Optional

from sqlalchemy import String, ForeignKey, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base


class UsageLog(Base):
    """
    Usage log model - tracks all billable operations.

    Features:
    - Per-job usage tracking
    - Monthly aggregation
    - Cost breakdown
    - Token usage
    """

    __tablename__ = "usage_logs"

    # Override id to use UUID
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Ownership
    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    project_id: Mapped[Optional[str]] = mapped_column(
        String,
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    job_id: Mapped[Optional[str]] = mapped_column(
        String,
        ForeignKey("generation_jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Usage details
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "generation", "export", etc.
    production_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Tokens & Cost
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, nullable=False)

    # Model breakdown (for analytics)
    mini_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    gpt4_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mini_cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    gpt4_cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationships
    # user = relationship("User", back_populates="usage_logs")
    # project = relationship("Project")
    # job = relationship("GenerationJob")

    def __repr__(self) -> str:
        return f"<UsageLog {self.operation_type} (${self.cost_usd:.2f})>"
