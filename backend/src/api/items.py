"""Items API endpoints for inventory management."""
from typing import Optional
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.services.stock_service import get_items_with_stock
from src.services.item_service import (
    check_name_unique,
    can_delete_item,
    get_unique_categories,
    get_unique_units,
)
from src.models.schemas import ItemWithStock, ItemCreate, ItemUpdate
from src.models.item import Item
from src.api.errors import ItemNotFound

router = APIRouter()


@router.get("/items", response_model=list[ItemWithStock])
async def list_items(
    search: Optional[str] = Query(None, description="Partial name search (case-insensitive)"),
    category: Optional[str] = Query(None, description="Exact category filter"),
    under_stock_only: bool = Query(False, description="Show only items with stock < min_stock"),
    sort_by: str = Query("name", description="Sort column (name, category, stock_quantity, is_under_min_stock)"),
    sort_order: str = Query("asc", description="Sort order (asc, desc)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all items with computed stock (FR-001).

    Filters:
    - search: Partial name search using pg_trgm index (FR-002)
    - category: Exact category match (FR-003)
    - under_stock_only: Show only items with stock < min_stock (FR-004)

    Sorting:
    - sort_by: name, category, stock_quantity, is_under_min_stock
    - sort_order: asc, desc

    Returns ItemWithStock array with real-time computed stock.
    """
    # T023: Validate query parameters
    valid_sort_by = ["name", "category", "stock_quantity", "is_under_min_stock"]
    valid_sort_order = ["asc", "desc"]

    if sort_by not in valid_sort_by:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Parametro sort_by non valido. Valori ammessi: {', '.join(valid_sort_by)}"
        )

    if sort_order.lower() not in valid_sort_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Parametro sort_order non valido. Valori ammessi: {', '.join(valid_sort_order)}"
        )

    # Query items with stock using service
    items = await get_items_with_stock(
        db=db,
        search=search,
        category=category,
        under_stock_only=under_stock_only,
        sort_by=sort_by,
        sort_order=sort_order.lower(),
    )

    return items


@router.post("/items", response_model=ItemWithStock, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ItemCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new item (FR-013).

    Validates:
    - Name is unique (case-insensitive)
    - min_stock >= 0
    - unit_cost >= 0

    Returns ItemWithStock with stock_quantity=0 (no movements yet).
    """
    # Check name uniqueness
    await check_name_unique(db, item_data.name)

    # Create new item
    new_item = Item(
        id=uuid4(),
        name=item_data.name.strip(),
        category=item_data.category.strip() if item_data.category else None,
        unit=item_data.unit,
        notes=item_data.notes,
        min_stock=item_data.min_stock,
        unit_cost=item_data.unit_cost,
    )

    db.add(new_item)
    await db.flush()

    # Return ItemWithStock format (stock_quantity=0 for new item)
    return ItemWithStock(
        id=new_item.id,
        name=new_item.name,
        category=new_item.category,
        unit=new_item.unit,
        notes=new_item.notes,
        min_stock=new_item.min_stock,
        unit_cost=new_item.unit_cost,
        stock_quantity="0",
        stock_value="0",
        is_under_min_stock=new_item.min_stock > 0,
        last_movement_at=None,
        created_at=new_item.created_at,
        updated_at=new_item.updated_at,
    )


@router.put("/items/{item_id}", response_model=ItemWithStock)
async def update_item(
    item_id: UUID,
    item_data: ItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing item (FR-014).

    Note: stock_quantity is read-only and can only be modified via movements.
    """
    # Get existing item
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()

    if not item:
        raise ItemNotFound(item_id=str(item_id))

    # Check name uniqueness if name is being changed
    if item_data.name and item_data.name.strip() != item.name:
        await check_name_unique(db, item_data.name, exclude_id=item_id)

    # Update fields (only if provided)
    if item_data.name:
        item.name = item_data.name.strip()
    if item_data.category is not None:
        item.category = item_data.category.strip() if item_data.category else None
    if item_data.unit:
        item.unit = item_data.unit
    if item_data.notes is not None:
        item.notes = item_data.notes
    if item_data.min_stock is not None:
        item.min_stock = item_data.min_stock
    if item_data.unit_cost is not None:
        item.unit_cost = item_data.unit_cost

    await db.flush()

    # Return updated item with current stock
    items = await get_items_with_stock(db)
    updated_item = next((i for i in items if str(i["id"]) == str(item_id)), None)

    if updated_item:
        return ItemWithStock(**updated_item)

    # Fallback if not found in stock view (shouldn't happen)
    raise ItemNotFound(item_id=str(item_id))


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an item (FR-015, FR-016, FR-017).

    Validation:
    - Item must have stock = 0 (FR-016)
    - Item must have no movements in last 12 months (FR-017)
    """
    # Get item
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()

    if not item:
        raise ItemNotFound(item_id=str(item_id))

    # Validate deletion is allowed
    await can_delete_item(db, item_id)

    # Delete item
    await db.delete(item)
    await db.flush()


@router.get("/items/autocomplete/categories")
async def autocomplete_categories(
    q: Optional[str] = Query(None, description="Search query for filtering"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get unique categories for autocomplete (FR-018).

    Returns list of existing categories, optionally filtered by search query.
    """
    categories = await get_unique_categories(db, search=q)
    return {"categories": categories}


@router.get("/items/autocomplete/units")
async def autocomplete_units(
    db: AsyncSession = Depends(get_db),
):
    """
    Get unique units for autocomplete (FR-018).

    Returns list of existing units.
    """
    units = await get_unique_units(db)
    return {"units": units}
