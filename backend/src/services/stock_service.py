"""Stock query service for current inventory with filters and sorting."""
from decimal import Decimal
from typing import Optional
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src.models.item import Item
from src.models.movement import Movement


async def get_items_with_stock(
    db: AsyncSession,
    search: Optional[str] = None,
    category: Optional[str] = None,
    under_stock_only: bool = False,
    sort_by: str = "name",
    sort_order: str = "asc",
) -> list[dict]:
    """
    Query items with computed stock from movements.

    Uses the current_stock view logic: aggregate movements by item_id.

    Args:
        db: Database session
        search: Partial name search (case-insensitive, uses pg_trgm index)
        category: Exact category match (None = all categories)
        under_stock_only: If True, only return items with stock < min_stock
        sort_by: Column to sort by (name, category, stock_quantity, is_under_min_stock)
        sort_order: Sort direction (asc, desc)

    Returns:
        List of ItemWithStock dictionaries
    """
    # Subquery for stock aggregation (mimics current_stock view)
    stock_subquery = (
        select(
            Movement.item_id,
            func.coalesce(func.sum(Movement.quantity), Decimal("0")).label("stock_quantity"),
            func.max(Movement.timestamp).label("last_movement_at"),
        )
        .group_by(Movement.item_id)
        .subquery()
    )

    # Main query joining items with stock aggregation
    query = (
        select(
            Item.id,
            Item.name,
            Item.category,
            Item.unit,
            Item.notes,
            Item.min_stock,
            Item.unit_cost,
            func.coalesce(stock_subquery.c.stock_quantity, Decimal("0")).label("stock_quantity"),
            (func.coalesce(stock_subquery.c.stock_quantity, Decimal("0")) * Item.unit_cost).label("stock_value"),
            (func.coalesce(stock_subquery.c.stock_quantity, Decimal("0")) < Item.min_stock).label("is_under_min_stock"),
            stock_subquery.c.last_movement_at,
            Item.created_at,
            Item.updated_at,
        )
        .outerjoin(stock_subquery, Item.id == stock_subquery.c.item_id)
    )

    # Apply filters
    filters = []

    # FR-002: Name search with pg_trgm (partial, case-insensitive)
    if search:
        # Use ILIKE for partial matching, pg_trgm index will optimize this
        filters.append(Item.name.ilike(f"%{search}%"))

    # FR-003: Category filter (exact match)
    if category:
        filters.append(Item.category == category)

    # FR-004: Under-stock toggle
    if under_stock_only:
        # Filter items where stock_quantity < min_stock
        filters.append(
            func.coalesce(stock_subquery.c.stock_quantity, Decimal("0")) < Item.min_stock
        )

    if filters:
        query = query.where(and_(*filters))

    # Apply sorting
    sort_column_map = {
        "name": Item.name,
        "category": Item.category,
        "stock_quantity": func.coalesce(stock_subquery.c.stock_quantity, Decimal("0")),
        "is_under_min_stock": (func.coalesce(stock_subquery.c.stock_quantity, Decimal("0")) < Item.min_stock),
    }

    sort_column = sort_column_map.get(sort_by, Item.name)

    if sort_order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Execute query
    result = await db.execute(query)
    rows = result.all()

    # Convert rows to dictionaries matching ItemWithStock schema
    items = []
    for row in rows:
        items.append({
            "id": row.id,
            "name": row.name,
            "category": row.category,
            "unit": row.unit,
            "notes": row.notes,
            "min_stock": row.min_stock,
            "unit_cost": row.unit_cost,
            "stock_quantity": row.stock_quantity,
            "stock_value": row.stock_value,
            "is_under_min_stock": row.is_under_min_stock,
            "last_movement_at": row.last_movement_at,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        })

    return items


async def get_dashboard_stats(db: AsyncSession) -> dict:
    """
    Calculate dashboard statistics.

    Returns:
        {
            "total_warehouse_value": Decimal (EUR),
            "under_stock_count": int,
            "total_items_count": int,
            "zero_stock_count": int
        }
    """
    # Subquery for stock aggregation
    stock_subquery = (
        select(
            Movement.item_id,
            func.coalesce(func.sum(Movement.quantity), Decimal("0")).label("stock_quantity"),
        )
        .group_by(Movement.item_id)
        .subquery()
    )

    # Query for statistics
    stats_query = select(
        # FR-041: Total warehouse value (SUM of stock_value for all items)
        func.coalesce(
            func.sum(
                func.coalesce(stock_subquery.c.stock_quantity, Decimal("0")) * Item.unit_cost
            ),
            Decimal("0")
        ).label("total_warehouse_value"),

        # FR-042: Under-stock count (COUNT WHERE stock < min_stock)
        func.count(
            func.case(
                (func.coalesce(stock_subquery.c.stock_quantity, Decimal("0")) < Item.min_stock, 1),
                else_=None
            )
        ).label("under_stock_count"),

        # Total items count
        func.count(Item.id).label("total_items_count"),

        # Zero stock count (items with no movements or stock = 0)
        func.count(
            func.case(
                (func.coalesce(stock_subquery.c.stock_quantity, Decimal("0")) == 0, 1),
                else_=None
            )
        ).label("zero_stock_count"),
    ).select_from(Item).outerjoin(stock_subquery, Item.id == stock_subquery.c.item_id)

    result = await db.execute(stats_query)
    row = result.one()

    return {
        "total_warehouse_value": row.total_warehouse_value,
        "under_stock_count": row.under_stock_count,
        "total_items_count": row.total_items_count,
        "zero_stock_count": row.zero_stock_count,
    }
