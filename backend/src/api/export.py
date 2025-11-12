"""Export API endpoints for Excel generation."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.services.export_service import get_export_data
from src.services.stock_service import get_items_with_stock
from src.services.movement_service import list_movements
from datetime import date, timedelta

router = APIRouter()


@router.get("/export/preview")
async def export_preview(
    db: AsyncSession = Depends(get_db),
):
    """
    Get export data for client-side Excel generation (FR-025-029).

    Returns:
    - export_date: Today's date
    - period_start/end: 12 months range
    - inventory: All items with stock
    - movements: Last 12 months movements with denormalized item names
    """
    from src.models.item import Item
    from sqlalchemy import select

    # Get export data
    twelve_months_ago = date.today() - timedelta(days=365)

    # Get items with stock
    items = await get_items_with_stock(db)

    # Get movements from last 12 months
    movements_data, _ = await list_movements(
        db=db,
        from_date=twelve_months_ago,
        to_date=date.today(),
        limit=10000,
    )

    # Convert movements to dicts with item names
    movements_export = []
    for movement in movements_data:
        # Get item name
        item_result = await db.execute(
            select(Item.name).where(Item.id == movement.item_id)
        )
        item_name = item_result.scalar_one()

        movements_export.append({
            "movement_date": movement.movement_date.isoformat(),
            "item_name": item_name,
            "movement_type": movement.movement_type,
            "quantity": str(movement.quantity),
            "unit_cost_override": str(movement.unit_cost_override) if movement.unit_cost_override else None,
            "note": movement.note,
        })

    return {
        "export_date": date.today().isoformat(),
        "period_start": twelve_months_ago.isoformat(),
        "period_end": date.today().isoformat(),
        "inventory": items,
        "movements": movements_export,
    }
