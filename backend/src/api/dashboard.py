"""Dashboard API endpoints for statistics and overview."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.services.stock_service import get_dashboard_stats
from src.models.schemas import DashboardStats

router = APIRouter()


@router.get("/dashboard/stats", response_model=DashboardStats)
async def dashboard_statistics(
    db: AsyncSession = Depends(get_db),
):
    """
    Get dashboard statistics (FR-041, FR-042).

    Returns:
    - total_warehouse_value: Total inventory value in EUR (SUM of stock_value)
    - under_stock_count: Number of items with stock < min_stock
    - total_items_count: Total number of items in catalog
    - zero_stock_count: Number of items with zero stock
    """
    stats = await get_dashboard_stats(db=db)
    return DashboardStats(**stats)
