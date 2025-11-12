"""Item service for CRUD operations and validation."""
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.item import Item
from src.models.movement import Movement
from src.api.errors import DuplicateItemName, ItemHasMovements, ItemHasStock


async def check_name_unique(
    db: AsyncSession,
    name: str,
    exclude_id: Optional[UUID] = None
) -> bool:
    """
    Check if item name is unique (case-insensitive) (FR-013).

    Args:
        db: Database session
        name: Item name to check
        exclude_id: Optional item ID to exclude (for updates)

    Returns:
        True if name is unique

    Raises:
        DuplicateItemName: If name already exists
    """
    query = select(Item).where(func.lower(Item.name) == func.lower(name.strip()))

    if exclude_id:
        query = query.where(Item.id != exclude_id)

    result = await db.execute(query)
    existing_item = result.scalar_one_or_none()

    if existing_item:
        raise DuplicateItemName(name=name.strip())

    return True


async def can_delete_item(
    db: AsyncSession,
    item_id: UUID
) -> tuple[bool, Optional[str]]:
    """
    Check if item can be deleted (FR-015, FR-016, FR-017).

    Business rules:
    - Cannot delete if stock > 0 (FR-016)
    - Cannot delete if has movements in last 12 months (FR-017)

    Args:
        db: Database session
        item_id: Item UUID

    Returns:
        (can_delete, error_message) tuple
    """
    # Get item with current stock
    from src.services.stock_service import get_items_with_stock
    from decimal import Decimal

    # Query current stock
    stock_result = await db.execute(
        select(func.coalesce(func.sum(Movement.quantity), Decimal("0")))
        .where(Movement.item_id == item_id)
    )
    current_stock = stock_result.scalar()

    # Get item for unit info
    item_result = await db.execute(select(Item).where(Item.id == item_id))
    item = item_result.scalar_one()

    # FR-016: Check stock is zero
    if current_stock != 0:
        raise ItemHasStock(
            item_id=str(item_id),
            current_stock=float(current_stock),
            unit=item.unit
        )

    # FR-017: Check no movements in last 12 months
    twelve_months_ago = datetime.now() - timedelta(days=365)
    movements_result = await db.execute(
        select(func.count(Movement.id))
        .where(Movement.item_id == item_id)
        .where(Movement.movement_date >= twelve_months_ago.date())
    )
    movement_count = movements_result.scalar()

    if movement_count > 0:
        raise ItemHasMovements(
            item_id=str(item_id),
            movement_count=movement_count
        )

    return True, None


async def get_unique_categories(
    db: AsyncSession,
    search: Optional[str] = None
) -> list[str]:
    """
    Get distinct categories for autocomplete (FR-018).

    Args:
        db: Database session
        search: Optional search filter

    Returns:
        List of unique category names (sorted)
    """
    query = select(Item.category).distinct().where(Item.category.isnot(None))

    if search:
        query = query.where(Item.category.ilike(f"%{search}%"))

    query = query.order_by(Item.category)

    result = await db.execute(query)
    categories = [row[0] for row in result.all()]

    return categories


async def get_unique_units(db: AsyncSession) -> list[str]:
    """
    Get distinct units for autocomplete (FR-018).

    Args:
        db: Database session

    Returns:
        List of unique unit names (sorted)
    """
    query = select(Item.unit).distinct().order_by(Item.unit)

    result = await db.execute(query)
    units = [row[0] for row in result.all()]

    return units
