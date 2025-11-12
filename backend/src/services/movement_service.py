"""Movement service for creating and managing inventory movements."""
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.item import Item
from src.models.movement import Movement
from src.api.errors import ItemNotFound, ValidationError


async def create_in_movement(
    db: AsyncSession,
    item_id: UUID,
    quantity: Decimal,
    movement_date: date,
    unit_cost_override: Optional[Decimal] = None,
    note: Optional[str] = None,
) -> Movement:
    """
    Create an IN movement (carico) with optional cost override (FR-006, FR-010, FR-011, FR-012).

    This function uses an ACID transaction to:
    1. Verify item exists (with row lock for concurrency)
    2. Insert movement record with positive quantity
    3. Update item.unit_cost if cost override provided
    4. Commit all changes atomically

    Args:
        db: Database session (transaction managed by caller)
        item_id: Item UUID
        quantity: Positive decimal quantity (already validated)
        movement_date: Date of movement
        unit_cost_override: Optional cost to update item's unit_cost
        note: Optional note

    Returns:
        Movement record

    Raises:
        ItemNotFound: If item_id does not exist
    """
    # FR-012: ACID transaction (BEGIN already started by get_db)
    # Lock item row for update to prevent race conditions
    result = await db.execute(
        select(Item).where(Item.id == item_id).with_for_update()
    )
    item = result.scalar_one_or_none()

    if not item:
        raise ItemNotFound(item_id=str(item_id))

    # Create IN movement with positive quantity
    movement = Movement(
        id=uuid4(),
        item_id=item_id,
        movement_type="IN",
        quantity=quantity,  # Positive for IN
        movement_date=movement_date,
        # FR-011: timestamp set by database server_default
        unit_cost_override=unit_cost_override,
        note=note,
    )

    db.add(movement)

    # FR-010: Update item unit_cost if override provided
    if unit_cost_override is not None:
        item.unit_cost = unit_cost_override

    # FR-012: COMMIT will be handled by get_db() context manager
    await db.flush()  # Ensure movement gets ID before returning

    return movement


async def create_out_movement(
    db: AsyncSession,
    item_id: UUID,
    quantity: Decimal,
    movement_date: date,
    note: Optional[str] = None,
) -> Movement:
    """
    Create an OUT movement (scarico) with stock validation (FR-007, FR-008).

    This function uses an ACID transaction to:
    1. Verify item exists (with row lock)
    2. Query current stock
    3. Validate sufficient stock
    4. Insert movement with negative quantity
    5. Commit atomically

    Args:
        db: Database session
        item_id: Item UUID
        quantity: Positive decimal (user input), will be negated
        movement_date: Date of movement
        note: Optional note

    Returns:
        Movement record

    Raises:
        ItemNotFound: If item_id does not exist
        InsufficientStock: If current stock < requested quantity
    """
    from src.api.errors import InsufficientStock
    from sqlalchemy import func

    # Lock item row
    result = await db.execute(
        select(Item).where(Item.id == item_id).with_for_update()
    )
    item = result.scalar_one_or_none()

    if not item:
        raise ItemNotFound(item_id=str(item_id))

    # FR-008: Query current stock (SUM of movements)
    stock_result = await db.execute(
        select(func.coalesce(func.sum(Movement.quantity), Decimal("0")))
        .where(Movement.item_id == item_id)
    )
    current_stock = stock_result.scalar()

    # FR-008: Validate sufficient stock
    if current_stock < quantity:
        raise InsufficientStock(
            requested_quantity=float(quantity),
            available_stock=float(current_stock),
            unit=item.unit,
        )

    # Create OUT movement with negative quantity
    movement = Movement(
        id=uuid4(),
        item_id=item_id,
        movement_type="OUT",
        quantity=-quantity,  # NEGATIVE for OUT
        movement_date=movement_date,
        unit_cost_override=None,  # Not applicable for OUT
        note=note,
    )

    db.add(movement)
    await db.flush()

    return movement


async def create_adjustment_movement(
    db: AsyncSession,
    item_id: UUID,
    target_stock: Decimal,
    movement_date: date,
    note: str,
) -> Movement:
    """
    Create an ADJUSTMENT movement (rettifica) with calculated delta (FR-036, FR-037, FR-038, FR-039, FR-040).

    This function:
    1. Verifies item exists
    2. Queries current stock
    3. Calculates delta (target - current)
    4. Validates delta != 0
    5. Inserts movement with calculated quantity (+/-)

    Args:
        db: Database session
        item_id: Item UUID
        target_stock: Desired final stock quantity
        movement_date: Date of adjustment
        note: MANDATORY explanation note

    Returns:
        Movement record with calculated quantity

    Raises:
        ItemNotFound: If item_id does not exist
        AdjustmentNotNeeded: If target == current stock
    """
    from src.api.errors import AdjustmentNotNeeded
    from sqlalchemy import func

    # Lock item row
    result = await db.execute(
        select(Item).where(Item.id == item_id).with_for_update()
    )
    item = result.scalar_one_or_none()

    if not item:
        raise ItemNotFound(item_id=str(item_id))

    # Query current stock
    stock_result = await db.execute(
        select(func.coalesce(func.sum(Movement.quantity), Decimal("0")))
        .where(Movement.item_id == item_id)
    )
    current_stock = stock_result.scalar()

    # FR-037: Calculate delta
    delta = target_stock - current_stock

    # FR-038: Validate delta != 0
    if delta == 0:
        raise AdjustmentNotNeeded(
            current_stock=float(current_stock),
            unit=item.unit,
        )

    # Create ADJUSTMENT movement with calculated delta (+/-)
    movement = Movement(
        id=uuid4(),
        item_id=item_id,
        movement_type="ADJUSTMENT",
        quantity=delta,  # Can be positive or negative
        movement_date=movement_date,
        unit_cost_override=None,
        note=note,  # FR-039: Note is mandatory (validated in schema)
    )

    db.add(movement)
    await db.flush()

    return movement


async def list_movements(
    db: AsyncSession,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    item_id: Optional[UUID] = None,
    movement_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[Movement], int]:
    """
    List movements with filters and pagination (FR-022, FR-023, FR-024).

    Args:
        db: Database session
        from_date: Start date filter (default: 30 days ago)
        to_date: End date filter (default: today)
        item_id: Optional item filter
        movement_type: Optional type filter (IN/OUT/ADJUSTMENT)
        limit: Max results to return
        offset: Pagination offset

    Returns:
        (movements list, total count) tuple
    """
    # Default date range: last 30 days
    if from_date is None:
        from_date = date.today() - timedelta(days=30)
    if to_date is None:
        to_date = date.today()

    # Build query with filters
    filters = [
        Movement.movement_date >= from_date,
        Movement.movement_date <= to_date,
    ]

    if item_id:
        filters.append(Movement.item_id == item_id)

    if movement_type and movement_type != "All":
        filters.append(Movement.movement_type == movement_type)

    # Query movements ordered by timestamp DESC (FR-024: most recent first)
    query = (
        select(Movement)
        .where(and_(*filters))
        .order_by(Movement.timestamp.desc())
    )

    # Get total count
    from sqlalchemy import func
    count_query = select(func.count()).select_from(Movement).where(and_(*filters))
    count_result = await db.execute(count_query)
    total_count = count_result.scalar()

    # Apply pagination
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    movements = result.scalars().all()

    return list(movements), total_count
