"""Movements API endpoints for IN/OUT/ADJUSTMENT operations."""
from datetime import date, datetime, timedelta
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.database import get_db
from src.services.movement_service import (
    create_in_movement,
    create_out_movement,
    create_adjustment_movement,
    list_movements,
)
from src.models.schemas import (
    MovementInCreate,
    MovementOutCreate,
    MovementAdjustmentCreate,
    MovementDetail,
)
from src.models.item import Item
from src.models.movement import Movement
from src.api.errors import (
    ValidationError,
    ConfirmationRequired,
    InvalidDateRange,
    ItemNotFound,
)

router = APIRouter()


async def validate_movement_date(movement_date: date, max_past_days: int = 365):
    """
    Validate movement date is within allowed range (FR-021 extension).

    Args:
        movement_date: Date to validate
        max_past_days: Maximum days in past/future allowed

    Raises:
        InvalidDateRange: If date is too far in past or future
    """
    today = date.today()
    min_date = today - timedelta(days=max_past_days)
    max_date = today + timedelta(days=max_past_days)

    if movement_date < min_date or movement_date > max_date:
        raise InvalidDateRange(
            movement_date=movement_date.isoformat(),
            max_past_days=max_past_days,
        )


async def get_item_name(db: AsyncSession, item_id: str) -> str:
    """Get item name for denormalized response."""
    result = await db.execute(
        select(Item.name).where(Item.id == item_id)
    )
    return result.scalar_one()


@router.post("/movements", response_model=MovementDetail, status_code=status.HTTP_201_CREATED)
async def create_movement(
    movement_in: MovementInCreate | MovementOutCreate | MovementAdjustmentCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a movement (IN/OUT/ADJUSTMENT) based on schema type.

    The movement type is inferred from the schema:
    - MovementInCreate -> IN
    - MovementOutCreate -> OUT
    - MovementAdjustmentCreate -> ADJUSTMENT

    Returns MovementDetail with denormalized item_name.
    """
    # Determine movement type from schema
    if isinstance(movement_in, MovementInCreate):
        # T035: Validation for IN movements
        await validate_movement_date(movement_in.movement_date)

        # Create IN movement
        movement = await create_in_movement(
            db=db,
            item_id=movement_in.item_id,
            quantity=movement_in.quantity,
            movement_date=movement_in.movement_date,
            unit_cost_override=movement_in.unit_cost_override,
            note=movement_in.note,
        )

    elif isinstance(movement_in, MovementOutCreate):
        # Validation for OUT movements
        await validate_movement_date(movement_in.movement_date)

        # FR-009: Confirmation required
        if not movement_in.confirmed:
            raise ConfirmationRequired(operation="scarico")

        # Create OUT movement
        movement = await create_out_movement(
            db=db,
            item_id=movement_in.item_id,
            quantity=movement_in.quantity,  # Service negates this
            movement_date=movement_in.movement_date,
            note=movement_in.note,
        )

    elif isinstance(movement_in, MovementAdjustmentCreate):
        # Validation for ADJUSTMENT movements
        await validate_movement_date(movement_in.movement_date)

        # Create ADJUSTMENT movement
        movement = await create_adjustment_movement(
            db=db,
            item_id=movement_in.item_id,
            target_stock=movement_in.target_stock,
            movement_date=movement_in.movement_date,
            note=movement_in.note,  # FR-039: Note mandatory (schema validates)
        )

    else:
        raise ValidationError(
            detail="Tipo movimento non riconosciuto",
            field="movement_type",
        )

    # Get item name for denormalized response
    item_name = await get_item_name(db, str(movement.item_id))

    # Return MovementDetail with denormalized fields
    return MovementDetail(
        id=movement.id,
        item_id=movement.item_id,
        item_name=item_name,
        movement_type=movement.movement_type,
        quantity=movement.quantity,
        movement_date=movement.movement_date,
        timestamp=movement.timestamp,
        unit_cost_override=movement.unit_cost_override,
        note=movement.note,
        created_by=None,  # Future: auth user
    )


@router.get("/movements", response_model=dict)
async def get_movements(
    from_date: Optional[date] = Query(None, description="Start date (default: 30 days ago)"),
    to_date: Optional[date] = Query(None, description="End date (default: today)"),
    item_id: Optional[UUID] = Query(None, description="Filter by item ID"),
    movement_type: Optional[str] = Query(None, description="Filter by type (IN/OUT/ADJUSTMENT/All)"),
    limit: int = Query(100, ge=1, le=500, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: AsyncSession = Depends(get_db),
):
    """
    List movements with filters and pagination (FR-022, FR-023, FR-024).

    Default: last 30 days, ordered by timestamp DESC (most recent first).
    """
    # T069: Date range filtering
    movements, total_count = await list_movements(
        db=db,
        from_date=from_date,
        to_date=to_date,
        item_id=item_id,
        movement_type=movement_type,
        limit=limit,
        offset=offset,
    )

    # Convert to MovementDetail format with denormalized item_name
    movement_details = []
    for movement in movements:
        item_name = await get_item_name(db, str(movement.item_id))
        movement_details.append(
            MovementDetail(
                id=movement.id,
                item_id=movement.item_id,
                item_name=item_name,
                movement_type=movement.movement_type,
                quantity=movement.quantity,
                movement_date=movement.movement_date,
                timestamp=movement.timestamp,
                unit_cost_override=movement.unit_cost_override,
                note=movement.note,
                created_by=None,
            )
        )

    return {
        "movements": movement_details,
        "total": total_count,
        "limit": limit,
        "offset": offset,
    }


@router.get("/movements/{movement_id}", response_model=MovementDetail)
async def get_movement_by_id(
    movement_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single movement by ID (FR-023).
    """
    result = await db.execute(select(Movement).where(Movement.id == movement_id))
    movement = result.scalar_one_or_none()

    if not movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movimento non trovato"
        )

    # Get item name for denormalized response
    item_name = await get_item_name(db, str(movement.item_id))

    return MovementDetail(
        id=movement.id,
        item_id=movement.item_id,
        item_name=item_name,
        movement_type=movement.movement_type,
        quantity=movement.quantity,
        movement_date=movement.movement_date,
        timestamp=movement.timestamp,
        unit_cost_override=movement.unit_cost_override,
        note=movement.note,
        created_by=None,
    )
