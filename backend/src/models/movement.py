"""Movement (Movimento) SQLAlchemy model - Immutable event log."""
import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Column, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.database import Base


class Movement(Base):
    """
    Movement (Movimento) - Immutable event log of inventory operations.

    Event-sourced architecture: movements are NEVER updated or deleted.
    Stock is computed as SUM(quantity) grouped by item_id.
    """

    __tablename__ = "movements"

    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )

    # Foreign key to item
    item_id = Column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="RESTRICT"),  # Prevent item deletion if movements exist
        nullable=False,
        index=True,  # idx_movements_item_id
    )

    # Movement details
    movement_type = Column(
        String(20),
        nullable=False,
        index=True,  # idx_movements_type
    )
    quantity = Column(
        Numeric(10, 3),  # Support 3 decimals for weights/volumes (FR-021)
        nullable=False,
    )
    movement_date = Column(
        Date,
        nullable=False,
        index=True,  # idx_movements_movement_date
    )

    # Timestamps (server-side, FR-011)
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        index=True,  # idx_movements_timestamp for DESC ordering
    )

    # Optional fields
    unit_cost_override = Column(
        Numeric(10, 2),
        nullable=True,
    )
    note = Column(Text, nullable=True)  # REQUIRED for ADJUSTMENT (app-level validation)
    created_by = Column(String(100), nullable=True)  # Future multi-user support

    # Relationships
    item = relationship("Item", back_populates="movements")

    # Constraints (FR-019, FR-006, FR-007, FR-039)
    __table_args__ = (
        # Basic validation
        CheckConstraint("quantity != 0", name="chk_movements_quantity_nonzero"),  # FR-019
        CheckConstraint(
            "movement_type IN ('IN', 'OUT', 'ADJUSTMENT')",
            name="chk_movements_type_valid",
        ),
        # Type-specific quantity constraints
        CheckConstraint(
            "movement_type != 'IN' OR quantity > 0",
            name="chk_movements_in_positive",  # FR-006
        ),
        CheckConstraint(
            "movement_type != 'OUT' OR quantity < 0",
            name="chk_movements_out_negative",  # FR-007
        ),
        # ADJUSTMENT note requirement (FR-039)
        CheckConstraint(
            "movement_type != 'ADJUSTMENT' OR (note IS NOT NULL AND LENGTH(TRIM(note)) > 0)",
            name="chk_movements_adjustment_note",
        ),
        # Unit cost override validation
        CheckConstraint(
            "unit_cost_override IS NULL OR unit_cost_override >= 0",
            name="chk_movements_cost_positive",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Movement(id={self.id}, type='{self.movement_type}', "
            f"quantity={self.quantity}, item_id={self.item_id})>"
        )
