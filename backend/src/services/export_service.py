"""Export service for Excel generation data."""
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.stock_service import get_items_with_stock
from src.services.movement_service import list_movements


async def get_export_data(db: AsyncSession) -> dict:
    """
    Get data for Excel export (FR-025, FR-026, FR-027, FR-028, FR-029).

    Returns inventory and last 12 months movements.
    """
    # Get all items with current stock
    items = await get_items_with_stock(db)

    # Get movements from last 12 months
    twelve_months_ago = date.today() - timedelta(days=365)
    movements, _ = await list_movements(
        db=db,
        from_date=twelve_months_ago,
        to_date=date.today(),
        limit=10000,  # High limit for export
    )

    return {
        "export_date": date.today().isoformat(),
        "period_start": twelve_months_ago.isoformat(),
        "period_end": date.today().isoformat(),
        "inventory": items,
        "movements": movements,
    }
