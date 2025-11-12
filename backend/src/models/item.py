"""Item (Articolo) SQLAlchemy model."""
import uuid
from datetime import datetime
from typing import List

from sqlalchemy import CheckConstraint, Column, DateTime, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.database import Base


class Item(Base):
    """
    Item (Articolo) - Master data for warehouse products/components.

    Stock quantity is NOT stored here but computed from movements.
    All movements reference items via foreign key.
    """

    __tablename__ = "items"

    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )

    # Core fields
    name = Column(String(255), nullable=False)  # FR-020: NOT NULL
    category = Column(String(100), nullable=True)  # Optional, autocomplete
    unit = Column(String(20), nullable=False, server_default="pz")  # Default "pz"
    notes = Column(Text, nullable=True)  # Optional descriptive notes

    # Stock management
    min_stock = Column(
        Numeric(10, 3),
        nullable=False,
        server_default="0",
    )
    unit_cost = Column(
        Numeric(10, 2),
        nullable=False,
        server_default="0",
    )

    # Timestamps (server-side, FR-011)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    # Relationships
    movements = relationship(
        "Movement",
        back_populates="item",
        cascade="restrict",  # FR-015: Prevent deletion if movements exist
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("min_stock >= 0", name="chk_items_min_stock_positive"),
        CheckConstraint("unit_cost >= 0", name="chk_items_unit_cost_positive"),
        CheckConstraint(
            "LENGTH(TRIM(name)) > 0", name="chk_items_name_not_empty"
        ),  # FR-020
    )

    def __repr__(self) -> str:
        return f"<Item(id={self.id}, name='{self.name}', category='{self.category}')>"
