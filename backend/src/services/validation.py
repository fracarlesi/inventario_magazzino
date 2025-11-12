"""Validation utilities for input data (T083.1).

Provides Italian error messages for validation failures per FR-021.
"""
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from src.api.errors import ValidationError, InvalidDateRange


def validate_decimal(
    value: str | float | Decimal,
    field_name: str,
    max_digits: int = 10,
    decimal_places: int = 3,
) -> Decimal:
    """
    Validate numeric format with max decimal places (FR-021).

    Args:
        value: Value to validate (string, float, or Decimal)
        field_name: Field name for error messages
        max_digits: Maximum total digits (default 10)
        decimal_places: Maximum decimal places (default 3)

    Returns:
        Validated Decimal value

    Raises:
        ValidationError: If value is not a valid decimal or exceeds limits
    """
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValidationError(
            detail=f"Il campo {field_name} deve essere un numero valido",
            field=field_name,
        )

    # Check for negative values
    if decimal_value < 0:
        raise ValidationError(
            detail=f"Il campo {field_name} deve essere maggiore o uguale a zero",
            field=field_name,
        )

    # Check decimal places
    decimal_tuple = decimal_value.as_tuple()
    if decimal_tuple.exponent < -decimal_places:
        raise ValidationError(
            detail=f"Il campo {field_name} può avere massimo {decimal_places} decimali",
            field=field_name,
        )

    # Check total digits
    total_digits = len(decimal_tuple.digits)
    if total_digits > max_digits:
        raise ValidationError(
            detail=f"Il campo {field_name} può avere massimo {max_digits} cifre",
            field=field_name,
        )

    return decimal_value


def validate_positive(
    value: str | float | Decimal,
    field_name: str,
) -> Decimal:
    """
    Validate that value is positive (> 0).

    Args:
        value: Value to validate
        field_name: Field name for error messages

    Returns:
        Validated Decimal value

    Raises:
        ValidationError: If value is not positive
    """
    decimal_value = validate_decimal(value, field_name)

    if decimal_value <= 0:
        raise ValidationError(
            detail=f"Il campo {field_name} deve essere maggiore di zero",
            field=field_name,
        )

    return decimal_value


def validate_date_range(
    movement_date: date,
    max_past_days: int = 365,
    allow_future: bool = False,
) -> date:
    """
    Validate movement date is within allowed range (FR-019 extended).

    Edge case decisions (from spec.md):
    - BLOCK if movement_date > TODAY (prevent accidental future dates)
    - BLOCK if movement_date < (TODAY - 365 days) (limit excessive backdating)

    Args:
        movement_date: Date to validate
        max_past_days: Maximum days in past allowed (default 365)
        allow_future: Whether future dates are allowed (default False)

    Returns:
        Validated date

    Raises:
        InvalidDateRange: If date is out of range
    """
    today = date.today()

    # Check future dates
    if not allow_future and movement_date > today:
        raise InvalidDateRange(
            movement_date=movement_date.isoformat(),
            max_past_days=max_past_days,
            detail="La data del movimento non può essere nel futuro",
        )

    # Check past dates
    min_date = today - timedelta(days=max_past_days)
    if movement_date < min_date:
        raise InvalidDateRange(
            movement_date=movement_date.isoformat(),
            max_past_days=max_past_days,
            detail=f"La data del movimento non può essere più di {max_past_days} giorni nel passato",
        )

    return movement_date


def validate_quantity(
    quantity: str | float | Decimal,
    movement_type: str,
) -> Decimal:
    """
    Validate quantity for movement (combines decimal + positive checks).

    Args:
        quantity: Quantity to validate
        movement_type: Type of movement (IN/OUT/ADJUSTMENT)

    Returns:
        Validated Decimal quantity

    Raises:
        ValidationError: If quantity is invalid
    """
    # For IN and OUT, quantity must be positive
    if movement_type in ["IN", "OUT"]:
        return validate_positive(quantity, "quantità")

    # For ADJUSTMENT, quantity can be positive or negative (delta)
    # but must be valid decimal
    return validate_decimal(quantity, "quantità")


def validate_non_empty_string(value: str | None, field_name: str) -> str:
    """
    Validate that string is not empty or whitespace-only (FR-020, FR-039).

    Args:
        value: String to validate
        field_name: Field name for error messages

    Returns:
        Stripped string

    Raises:
        ValidationError: If string is empty or None
    """
    if not value or not value.strip():
        raise ValidationError(
            detail=f"Il campo {field_name} è obbligatorio e non può essere vuoto",
            field=field_name,
        )

    return value.strip()


def validate_note_required(note: str | None) -> str:
    """
    Validate that note is provided and non-empty (FR-039 for ADJUSTMENT).

    Args:
        note: Note text to validate

    Returns:
        Stripped note text

    Raises:
        ValidationError: If note is missing or empty
    """
    if not note or not note.strip():
        raise ValidationError(
            detail="La nota è obbligatoria per le rettifiche (spiega il motivo della discrepanza)",
            field="note",
        )

    return note.strip()
