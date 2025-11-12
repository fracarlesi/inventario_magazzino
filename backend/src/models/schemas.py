"""Pydantic schemas for request/response validation."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ========== Item Schemas ==========

class ItemCreate(BaseModel):
    """Schema for creating a new item."""
    name: str = Field(..., min_length=1, max_length=255, description="Item name (non-empty)")
    category: Optional[str] = Field(None, max_length=100, description="Category (optional, autocomplete)")
    unit: str = Field(default="pz", max_length=20, description="Unit of measure")
    notes: Optional[str] = Field(None, description="Additional notes")
    min_stock: Decimal = Field(default=Decimal("0"), ge=0, description="Minimum stock threshold")
    unit_cost: Decimal = Field(default=Decimal("0"), ge=0, description="Unit cost (can be 0)")

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Il nome dell'articolo non può essere vuoto")
        return v.strip()


class ItemUpdate(BaseModel):
    """Schema for updating an item (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None
    min_stock: Optional[Decimal] = Field(None, ge=0)
    unit_cost: Optional[Decimal] = Field(None, ge=0)

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v or not v.strip()):
            raise ValueError("Il nome dell'articolo non può essere vuoto")
        return v.strip() if v else None


class ItemWithStock(BaseModel):
    """Schema for item with computed stock (from current_stock view)."""
    id: UUID
    name: str
    category: Optional[str]
    unit: str
    notes: Optional[str]
    min_stock: Decimal
    unit_cost: Decimal
    stock_quantity: Decimal  # Computed from movements
    stock_value: Decimal  # stock_quantity * unit_cost
    is_under_min_stock: bool  # stock_quantity < min_stock
    last_movement_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy


# ========== Movement Schemas ==========

class MovementInCreate(BaseModel):
    """Schema for creating an IN movement (carico)."""
    item_id: UUID
    quantity: Decimal = Field(..., gt=0, description="Quantity to load (must be positive)")
    movement_date: date = Field(default_factory=date.today, description="Movement date (default today)")
    unit_cost_override: Optional[Decimal] = Field(None, ge=0, description="Override item unit cost")
    note: Optional[str] = Field(None, description="Optional note")

    @field_validator('quantity')
    @classmethod
    def validate_quantity_format(cls, v: Decimal) -> Decimal:
        """FR-021: Max 3 decimal places."""
        if v.as_tuple().exponent < -3:
            raise ValueError("La quantità può avere massimo 3 cifre decimali")
        return v


class MovementOutCreate(BaseModel):
    """Schema for creating an OUT movement (scarico)."""
    item_id: UUID
    quantity: Decimal = Field(..., gt=0, description="Quantity to unload (user inputs positive)")
    movement_date: date = Field(default_factory=date.today, description="Movement date (default today)")
    note: Optional[str] = Field(None, description="Optional note")
    confirmed: bool = Field(..., description="Confirmation required (FR-009)")

    @field_validator('quantity')
    @classmethod
    def validate_quantity_format(cls, v: Decimal) -> Decimal:
        """FR-021: Max 3 decimal places."""
        if v.as_tuple().exponent < -3:
            raise ValueError("La quantità può avere massimo 3 cifre decimali")
        return v


class MovementAdjustmentCreate(BaseModel):
    """Schema for creating an ADJUSTMENT movement (rettifica)."""
    item_id: UUID
    target_stock: Decimal = Field(..., ge=0, description="Target stock quantity (system calculates delta)")
    movement_date: date = Field(default_factory=date.today, description="Movement date (default today)")
    note: str = Field(..., min_length=1, description="Mandatory note for adjustment (FR-039)")

    @field_validator('target_stock')
    @classmethod
    def validate_target_stock_format(cls, v: Decimal) -> Decimal:
        """FR-021: Max 3 decimal places."""
        if v.as_tuple().exponent < -3:
            raise ValueError("La giacenza target può avere massimo 3 cifre decimali")
        return v

    @field_validator('note')
    @classmethod
    def note_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("La nota è obbligatoria per le rettifiche")
        return v.strip()


class MovementDetail(BaseModel):
    """Schema for movement details (response)."""
    id: UUID
    item_id: UUID
    item_name: str  # Denormalized for display
    movement_type: str  # IN, OUT, ADJUSTMENT
    quantity: Decimal
    movement_date: date
    timestamp: datetime
    unit_cost_override: Optional[Decimal]
    note: Optional[str]
    created_by: Optional[str]

    class Config:
        from_attributes = True


# ========== Error Schemas ==========

class ErrorResponse(BaseModel):
    """Standard error response schema."""
    detail: str = Field(..., description="Human-readable error message (Italian)")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")
    context: Optional[dict] = Field(None, description="Additional error context")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Impossibile scaricare 10 unità. Giacenza disponibile: 5 pz",
                "error_code": "INSUFFICIENT_STOCK",
                "context": {
                    "requested_quantity": 10,
                    "available_stock": 5,
                    "unit": "pz"
                }
            }
        }


# ========== Dashboard Schemas ==========

class DashboardStats(BaseModel):
    """Schema for dashboard statistics."""
    total_warehouse_value: Decimal = Field(..., description="Total inventory value (EUR)")
    under_stock_count: int = Field(..., description="Number of items below min_stock")
    total_items_count: int = Field(..., description="Total number of items")
    zero_stock_count: int = Field(..., description="Number of items with zero stock")


# ========== Autocomplete Schemas ==========

class AutocompleteResponse(BaseModel):
    """Schema for autocomplete suggestions."""
    suggestions: list[str] = Field(..., description="List of suggestions")
