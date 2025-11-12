"""Custom exceptions and error handling utilities with Italian error messages."""
from typing import Any, Optional


class InventoryException(Exception):
    """Base exception for inventory management errors."""

    def __init__(
        self,
        detail: str,
        error_code: Optional[str] = None,
        context: Optional[dict[str, Any]] = None
    ):
        self.detail = detail
        self.error_code = error_code
        self.context = context or {}
        super().__init__(self.detail)


class ItemNotFound(InventoryException):
    """Raised when an item does not exist."""

    def __init__(self, item_id: str):
        super().__init__(
            detail=f"Articolo con ID {item_id} non trovato",
            error_code="ITEM_NOT_FOUND",
            context={"item_id": item_id}
        )


class InsufficientStock(InventoryException):
    """Raised when attempting to unload more stock than available (FR-008)."""

    def __init__(
        self,
        requested_quantity: float,
        available_stock: float,
        unit: str = "pz"
    ):
        super().__init__(
            detail=f"Impossibile scaricare {requested_quantity} unità. Giacenza disponibile: {available_stock} {unit}",
            error_code="INSUFFICIENT_STOCK",
            context={
                "requested_quantity": requested_quantity,
                "available_stock": available_stock,
                "unit": unit
            }
        )


class ValidationError(InventoryException):
    """Raised when input validation fails."""

    def __init__(self, detail: str, field: Optional[str] = None):
        super().__init__(
            detail=detail,
            error_code="VALIDATION_ERROR",
            context={"field": field} if field else {}
        )


class DuplicateItemName(InventoryException):
    """Raised when attempting to create item with duplicate name."""

    def __init__(self, name: str):
        super().__init__(
            detail=f"Esiste già un articolo con il nome '{name}'",
            error_code="DUPLICATE_ITEM_NAME",
            context={"name": name}
        )


class ItemHasMovements(InventoryException):
    """Raised when attempting to delete item with existing movements (FR-015)."""

    def __init__(self, item_id: str, movement_count: int):
        super().__init__(
            detail=f"Impossibile eliminare l'articolo: esistono {movement_count} movimenti associati",
            error_code="ITEM_HAS_MOVEMENTS",
            context={"item_id": item_id, "movement_count": movement_count}
        )


class ItemHasStock(InventoryException):
    """Raised when attempting to delete item with non-zero stock (FR-016)."""

    def __init__(self, item_id: str, current_stock: float, unit: str = "pz"):
        super().__init__(
            detail=f"Impossibile eliminare l'articolo: giacenza attuale {current_stock} {unit}. Scaricare prima di eliminare.",
            error_code="ITEM_HAS_STOCK",
            context={
                "item_id": item_id,
                "current_stock": current_stock,
                "unit": unit
            }
        )


class ConfirmationRequired(InventoryException):
    """Raised when operation requires explicit user confirmation (FR-009)."""

    def __init__(self, operation: str = "scarico"):
        super().__init__(
            detail=f"Conferma richiesta per {operation}",
            error_code="CONFIRMATION_REQUIRED",
            context={"operation": operation}
        )


class AdjustmentNotNeeded(InventoryException):
    """Raised when adjustment target equals current stock (FR-038)."""

    def __init__(self, current_stock: float, unit: str = "pz"):
        super().__init__(
            detail=f"Nessuna rettifica necessaria: la giacenza è già {current_stock} {unit}",
            error_code="ADJUSTMENT_NOT_NEEDED",
            context={"current_stock": current_stock, "unit": unit}
        )


class InvalidDateRange(InventoryException):
    """Raised when movement date is outside allowed range."""

    def __init__(self, movement_date: str, max_past_days: int = 365):
        super().__init__(
            detail=f"Data movimento non valida: {movement_date}. La data non può essere superiore a {max_past_days} giorni nel passato o nel futuro",
            error_code="INVALID_DATE_RANGE",
            context={
                "movement_date": movement_date,
                "max_past_days": max_past_days
            }
        )
