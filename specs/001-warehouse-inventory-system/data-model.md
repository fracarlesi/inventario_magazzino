# Data Model: Warehouse Inventory System

**Feature Branch**: `001-warehouse-inventory-system`
**Created**: 2025-11-11
**Database**: PostgreSQL 15+
**ORM**: SQLAlchemy 2.x
**Architecture**: Event-sourced (immutable movements, computed stock)

## Overview

This data model implements an **event-sourced architecture** for warehouse inventory management. Instead of directly updating stock quantities, all warehouse operations are recorded as immutable movement events (IN, OUT, ADJUSTMENT). Current stock levels are computed on-the-fly by aggregating these movements.

### Key Design Principles

1. **Immutability**: Movement records are never updated or deleted after creation
2. **Auditability**: Complete historical trail of all inventory operations
3. **Computed State**: Stock quantities are derived from movements, not stored
4. **Data Integrity**: Constraints prevent negative stock and invalid operations
5. **Performance**: Indexed queries and materialized views for fast reads

### Two-Table Pattern

- **`items`**: Master data for products/components (name, category, cost, etc.)
- **`movements`**: Immutable event log of all inventory operations (IN/OUT/ADJUSTMENT)
- **`current_stock`** (view): Real-time computed stock by aggregating movements

## Entities

### Item (Articolo)

Represents a product or component stored in the warehouse. Items are the master data entities that movements reference. The stock quantity is NOT stored here but computed from movements.

**Table: items**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| `name` | VARCHAR(255) | NOT NULL | Item name (e.g., "Olio motore 5W30") |
| `category` | VARCHAR(100) | NULL | Free-text category with autocomplete (e.g., "Filtri olio") |
| `unit` | VARCHAR(20) | NOT NULL, DEFAULT 'pz' | Unit of measure (e.g., "pz", "kg", "lt", "m") |
| `notes` | TEXT | NULL | Descriptive notes or additional info |
| `min_stock` | NUMERIC(10,3) | NOT NULL, DEFAULT 0, CHECK (min_stock >= 0) | Minimum stock threshold for alerts |
| `unit_cost` | NUMERIC(10,2) | NOT NULL, DEFAULT 0, CHECK (unit_cost >= 0) | Current unit cost (can be 0 for free items) |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp (server-side) |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp (server-side) |

**Indexes:**
```sql
CREATE INDEX idx_items_name ON items USING GIN (name gin_trgm_ops);  -- Full-text search
CREATE INDEX idx_items_category ON items (category);                 -- Category filtering
CREATE INDEX idx_items_created_at ON items (created_at DESC);        -- Recent items
```

**Validation Rules:**
- FR-020: `name` must be non-empty (NOT NULL constraint)
- FR-021: `min_stock` and `unit_cost` must be valid numeric values >= 0
- Assumption: `unit_cost` can be 0 for free/recovered items
- Assumption: `category` is optional (NULL allowed)

**Business Rules:**
- FR-013: New items start with computed stock = 0 (no movements yet)
- FR-014: All fields editable except stock (modified via movements only)
- FR-015: Deletion allowed only if: `current_stock = 0` AND no movements in last 12 months
- FR-016: Deletion blocked if `current_stock > 0`
- FR-017: Deletion blocked if movements exist in last 12 months
- Assumption: Deleted items preserve their old movements for audit (soft delete or cascade preserve)

---

### Movement (Movimento)

Immutable event log representing inventory operations. Each movement records a specific change (load, unload, adjustment) to an item's stock. Movements are NEVER updated or deleted after creation.

**Table: movements**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| `item_id` | UUID | NOT NULL, FOREIGN KEY REFERENCES items(id) ON DELETE RESTRICT | Reference to item |
| `movement_type` | VARCHAR(20) | NOT NULL, CHECK (movement_type IN ('IN', 'OUT', 'ADJUSTMENT')) | Operation type |
| `quantity` | NUMERIC(10,3) | NOT NULL, CHECK (quantity != 0) | Quantity change (see notes) |
| `movement_date` | DATE | NOT NULL | Operation date (default today, can be past) |
| `timestamp` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Server-side creation timestamp |
| `unit_cost_override` | NUMERIC(10,2) | NULL, CHECK (unit_cost_override >= 0) | Override cost for IN movements |
| `note` | TEXT | NULL | Optional note (REQUIRED for ADJUSTMENT) |
| `created_by` | VARCHAR(100) | NULL | User identifier (future multi-user support) |

**Indexes:**
```sql
CREATE INDEX idx_movements_item_id ON movements (item_id);                    -- Lookup by item
CREATE INDEX idx_movements_timestamp ON movements (timestamp DESC);           -- Recent movements
CREATE INDEX idx_movements_movement_date ON movements (movement_date DESC);   -- Date filtering
CREATE INDEX idx_movements_type ON movements (movement_type);                 -- Filter by type
CREATE INDEX idx_movements_item_date ON movements (item_id, movement_date DESC);  -- Item history
```

**Quantity Field Semantics:**

- **IN movements**: `quantity > 0` (e.g., +20 units loaded)
- **OUT movements**: `quantity < 0` (e.g., -5 units unloaded)
- **ADJUSTMENT movements**: `quantity` can be positive or negative (e.g., -2 for shrinkage, +5 for found items)

This design allows simple SUM aggregation: `current_stock = SUM(quantity) GROUP BY item_id`

**Validation Rules:**
- FR-019: Quantity must be non-zero (`CHECK (quantity != 0)`)
- FR-021: Quantity must be valid numeric with up to 3 decimals (support for weights/volumes)
- FR-011: Timestamp is server-side (`DEFAULT CURRENT_TIMESTAMP`)
- FR-039: Note is REQUIRED for ADJUSTMENT movements (application-level validation)
- Assumption: Movement dates cannot be >365 days past or future (application validation)

**Business Rules:**
- FR-006: IN movements require `quantity > 0`, optional `unit_cost_override`, optional `note`
- FR-007: OUT movements require `quantity < 0`, optional `note`
- FR-008: OUT movements blocked if resulting stock would be negative (pre-insert validation)
- FR-009: OUT movements require explicit user confirmation before insert
- FR-010: If `unit_cost_override` is set on IN movement, update `items.unit_cost` after insert
- FR-012: All movements are atomic (database transactions)
- FR-036: ADJUSTMENT movements calculated as `quantity = target_stock - current_stock`
- FR-037: System auto-calculates ADJUSTMENT quantity (user provides target, not delta)
- FR-038: ADJUSTMENT blocked if `target_stock = current_stock`
- FR-039: ADJUSTMENT requires non-empty `note` field
- FR-040: ADJUSTMENT shown in history with visible delta sign (+/-)
- Assumption: ADJUSTMENT cannot result in negative stock (validate before insert)

**State Transitions:**

```
[User Action: Carico]
  → Validate quantity > 0
  → Check current_stock (optional, informational)
  → INSERT movement (type=IN, quantity=+X)
  → IF unit_cost_override: UPDATE items SET unit_cost
  → COMMIT transaction
  → Recompute current_stock (via view)

[User Action: Scarico]
  → Validate quantity > 0 (user inputs positive, stored as negative)
  → Check current_stock >= quantity (MUST pass)
  → Show confirmation dialog with current stock
  → INSERT movement (type=OUT, quantity=-X)
  → COMMIT transaction
  → Recompute current_stock (via view)
  → Check if new stock < min_stock → trigger alert

[User Action: Rettifica]
  → User provides target_stock and note
  → Calculate quantity = target_stock - current_stock
  → Validate quantity != 0 (block if no change needed)
  → Validate note is non-empty (required)
  → Validate target_stock >= 0 (no negative stock)
  → INSERT movement (type=ADJUSTMENT, quantity=calculated_delta, note=required)
  → COMMIT transaction
  → Recompute current_stock (via view)
```

---

## Computed Views

### current_stock

Real-time materialized view computing current stock levels by aggregating all movements per item. This is the source of truth for "giacenza corrente" displayed in the dashboard.

**View Definition:**

```sql
CREATE OR REPLACE VIEW current_stock AS
SELECT
    i.id AS item_id,
    i.name AS item_name,
    i.category,
    i.unit,
    i.min_stock,
    i.unit_cost,
    i.notes,
    COALESCE(SUM(m.quantity), 0) AS stock_quantity,
    COALESCE(SUM(m.quantity), 0) * i.unit_cost AS stock_value,
    CASE
        WHEN COALESCE(SUM(m.quantity), 0) < i.min_stock THEN TRUE
        ELSE FALSE
    END AS is_under_min_stock,
    MAX(m.timestamp) AS last_movement_at
FROM items i
LEFT JOIN movements m ON m.item_id = i.id
GROUP BY i.id, i.name, i.category, i.unit, i.min_stock, i.unit_cost, i.notes;
```

**Columns:**
- `item_id`: Item identifier
- `item_name`: Item name (for display)
- `category`: Item category (for filtering)
- `unit`: Unit of measure
- `min_stock`: Minimum stock threshold
- `unit_cost`: Current unit cost
- `notes`: Item notes
- `stock_quantity`: Computed current stock = SUM(movements.quantity)
- `stock_value`: Computed value = stock_quantity × unit_cost
- `is_under_min_stock`: Boolean flag for under-threshold alert
- `last_movement_at`: Timestamp of most recent movement (for sorting/audit)

**Usage:**
- FR-001: Dashboard displays `stock_quantity` in real-time
- FR-004: Filter `WHERE is_under_min_stock = TRUE` for under-stock view
- FR-005: Visual highlighting based on `is_under_min_stock` flag
- FR-041: Total warehouse value = `SUM(stock_value)`
- FR-042: Under-stock count = `COUNT(*) WHERE is_under_min_stock = TRUE`

**Performance Considerations:**
- For small datasets (<1000 items), compute on-the-fly from view
- For larger datasets (>10k movements), consider materialized view with REFRESH
- Alternative: Maintain denormalized `items.cached_stock` updated via triggers (if needed)

---

## Relationships

### Entity Relationship Diagram

```
┌─────────────────────────────────────┐
│             items                   │
├─────────────────────────────────────┤
│ PK  id (UUID)                       │
│     name (VARCHAR)                  │
│     category (VARCHAR)              │
│     unit (VARCHAR)                  │
│     notes (TEXT)                    │
│     min_stock (NUMERIC)             │
│     unit_cost (NUMERIC)             │
│     created_at (TIMESTAMPTZ)        │
│     updated_at (TIMESTAMPTZ)        │
└─────────────────────────────────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────────────────────────┐
│           movements                 │
├─────────────────────────────────────┤
│ PK  id (UUID)                       │
│ FK  item_id → items.id              │
│     movement_type (VARCHAR)         │
│     quantity (NUMERIC)              │
│     movement_date (DATE)            │
│     timestamp (TIMESTAMPTZ)         │
│     unit_cost_override (NUMERIC)    │
│     note (TEXT)                     │
│     created_by (VARCHAR)            │
└─────────────────────────────────────┘
         │
         │ Aggregation
         │ (SUM quantity)
         ▼
┌─────────────────────────────────────┐
│        current_stock (VIEW)         │
├─────────────────────────────────────┤
│     item_id                         │
│     item_name                       │
│     stock_quantity (computed)       │
│     stock_value (computed)          │
│     is_under_min_stock (computed)   │
│     last_movement_at (computed)     │
└─────────────────────────────────────┘
```

### Foreign Key Constraints

**movements.item_id → items.id**
- Constraint: `FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE RESTRICT`
- Behavior: Prevent deletion of items that have movements (preserves audit trail)
- FR-015: Application must check for movements before allowing item deletion
- Assumption: Even deleted items preserve their movement history

### Cardinality

- **items ↔ movements**: One-to-Many
  - One item can have many movements (0..∞)
  - Each movement belongs to exactly one item (1)

- **items ↔ current_stock**: One-to-One
  - Each item has exactly one computed stock entry in the view
  - The view always includes all items (LEFT JOIN ensures items with 0 movements appear)

---

## Indexes

### Performance Optimization Strategy

The application has specific query patterns that drive index design:

1. **Dashboard inventory view**: Filter by category, search by name, sort by under-stock
2. **Movement history**: Filter by date range, item, type, paginate results
3. **Stock computation**: Aggregate movements by item_id
4. **Autocomplete**: Suggest categories and units from existing values

### Index Specifications

**items table:**

```sql
-- Primary key (automatic)
CREATE UNIQUE INDEX items_pkey ON items (id);

-- Full-text search on name (FR-002: partial matching, case-insensitive)
CREATE INDEX idx_items_name_trgm ON items USING GIN (name gin_trgm_ops);

-- Category filtering (FR-003)
CREATE INDEX idx_items_category ON items (category) WHERE category IS NOT NULL;

-- Recent items (sorting, audit)
CREATE INDEX idx_items_created_at ON items (created_at DESC);

-- Under-stock queries (needs current_stock view, but can pre-filter items)
CREATE INDEX idx_items_min_stock ON items (min_stock) WHERE min_stock > 0;
```

**movements table:**

```sql
-- Primary key (automatic)
CREATE UNIQUE INDEX movements_pkey ON movements (id);

-- Foreign key lookup (critical for aggregation and joins)
CREATE INDEX idx_movements_item_id ON movements (item_id);

-- Recent movements display (FR-022, FR-024: default last 30 days, DESC order)
CREATE INDEX idx_movements_timestamp ON movements (timestamp DESC);

-- Date range filtering (FR-022: filter by movement_date)
CREATE INDEX idx_movements_movement_date ON movements (movement_date DESC);

-- Type filtering (FR-022: filter IN/OUT/ADJUSTMENT)
CREATE INDEX idx_movements_type ON movements (movement_type);

-- Composite: item history (efficient for per-item movement queries)
CREATE INDEX idx_movements_item_date ON movements (item_id, movement_date DESC);

-- Export filtering (FR-028: last 12 months)
CREATE INDEX idx_movements_export_range ON movements (movement_date DESC)
    WHERE movement_date >= CURRENT_DATE - INTERVAL '12 months';
```

**Note on trigram indexes**: The `gin_trgm_ops` index requires PostgreSQL extension:
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

### Query Patterns and Index Usage

| Query | Indexes Used | Requirement |
|-------|--------------|-------------|
| Dashboard inventory list | `current_stock` view (aggregates via `idx_movements_item_id`) | FR-001 |
| Search items by name | `idx_items_name_trgm` | FR-002 |
| Filter by category | `idx_items_category` | FR-003 |
| Under-stock filter | `current_stock WHERE is_under_min_stock = TRUE` | FR-004 |
| Recent movements (30d) | `idx_movements_timestamp` | FR-022, FR-024 |
| Filter movements by date | `idx_movements_movement_date` | FR-022 |
| Filter movements by type | `idx_movements_type` | FR-022 |
| Item movement history | `idx_movements_item_date` | Item detail page |
| Export last 12 months | `idx_movements_export_range` | FR-028 |
| Autocomplete categories | `idx_items_category` + `DISTINCT` | FR-018 |

---

## Validation Rules

### Database-Level Constraints

**items table:**
```sql
-- Non-null name (FR-020)
ALTER TABLE items ADD CONSTRAINT chk_items_name_not_empty
    CHECK (LENGTH(TRIM(name)) > 0);

-- Non-negative min_stock (business logic)
ALTER TABLE items ADD CONSTRAINT chk_items_min_stock_positive
    CHECK (min_stock >= 0);

-- Non-negative unit_cost (FR-021, allows 0 for free items)
ALTER TABLE items ADD CONSTRAINT chk_items_unit_cost_positive
    CHECK (unit_cost >= 0);

-- Valid unit (non-empty if not NULL)
ALTER TABLE items ADD CONSTRAINT chk_items_unit_not_empty
    CHECK (LENGTH(TRIM(unit)) > 0);
```

**movements table:**
```sql
-- Valid movement type (FR-006, FR-007, FR-036)
ALTER TABLE movements ADD CONSTRAINT chk_movements_type_valid
    CHECK (movement_type IN ('IN', 'OUT', 'ADJUSTMENT'));

-- Non-zero quantity (FR-019, FR-037)
ALTER TABLE movements ADD CONSTRAINT chk_movements_quantity_nonzero
    CHECK (quantity != 0);

-- Non-negative unit_cost_override if present (FR-021)
ALTER TABLE movements ADD CONSTRAINT chk_movements_cost_positive
    CHECK (unit_cost_override IS NULL OR unit_cost_override >= 0);

-- Movement type constraints (enforced at insert)
-- IN: quantity must be positive
ALTER TABLE movements ADD CONSTRAINT chk_movements_in_positive
    CHECK (movement_type != 'IN' OR quantity > 0);

-- OUT: quantity must be negative
ALTER TABLE movements ADD CONSTRAINT chk_movements_out_negative
    CHECK (movement_type != 'OUT' OR quantity < 0);

-- unit_cost_override only for IN movements
ALTER TABLE movements ADD CONSTRAINT chk_movements_cost_in_only
    CHECK (unit_cost_override IS NULL OR movement_type = 'IN');
```

### Application-Level Validations

These rules must be enforced in the application layer (Python/SQLAlchemy):

**Before INSERT movement:**

1. **FR-008**: For OUT movements, check `current_stock + quantity >= 0`
   - Query current stock from `current_stock` view
   - Block if resulting stock would be negative
   - Error message: "Impossibile scaricare X unità. Giacenza disponibile: Y"

2. **FR-038**: For ADJUSTMENT movements, check `target_stock != current_stock`
   - Calculate `quantity = target_stock - current_stock`
   - Block if delta is 0
   - Error message: "La giacenza target coincide con quella attuale. Nessuna rettifica necessaria."

3. **FR-039**: For ADJUSTMENT movements, validate note is non-empty
   - Block if `note IS NULL OR LENGTH(TRIM(note)) = 0`
   - Error message: "La nota è obbligatoria per le rettifiche (spiega il motivo della discrepanza)"

4. **Assumption**: Validate movement_date is not >365 days past or in future
   - Block if `movement_date > CURRENT_DATE`
   - Block if `movement_date < CURRENT_DATE - INTERVAL '365 days'`

5. **Assumption**: For ADJUSTMENT, validate target_stock >= 0 (no negative stock)
   - Error message: "La giacenza target non può essere negativa"

**Before DELETE item:**

1. **FR-015**: Check deletion eligibility
   - Query `current_stock.stock_quantity` for item
   - Block if `stock_quantity > 0` (FR-016)
   - Error message: "Impossibile eliminare: giacenza non zero"

2. **FR-017**: Check for recent movements
   - Query `movements WHERE item_id = ? AND movement_date >= CURRENT_DATE - INTERVAL '12 months'`
   - Block if any exist
   - Error message: "Impossibile eliminare: l'articolo ha movimenti recenti (ultimi 12 mesi)"

**After INSERT movement (IN with unit_cost_override):**

1. **FR-010**: Update item unit cost
   - If `movement.unit_cost_override IS NOT NULL` and `movement_type = 'IN'`
   - Execute: `UPDATE items SET unit_cost = movement.unit_cost_override WHERE id = movement.item_id`

### Data Type Validations (SQLAlchemy Models)

```python
# Numeric fields with precision
min_stock = Column(Numeric(10, 3))      # Up to 9999999.999
unit_cost = Column(Numeric(10, 2))      # Up to 99999999.99
quantity = Column(Numeric(10, 3))       # Support decimals (e.g., 2.500 kg)

# String length limits
name = Column(String(255), nullable=False)
category = Column(String(100))
unit = Column(String(20), default='pz')
movement_type = Column(String(20))

# Text fields (no limit)
notes = Column(Text)
note = Column(Text)  # For movements

# Timestamps (all timezone-aware)
created_at = Column(DateTime(timezone=True), server_default=func.now())
timestamp = Column(DateTime(timezone=True), server_default=func.now())
```

---

## Event Sourcing Implementation

### Architecture Overview

This system implements a **simplified event sourcing pattern** optimized for single-user warehouse management:

- **Event Store**: `movements` table is the append-only event log
- **Read Model**: `current_stock` view is the computed projection
- **Write Model**: Items table holds mutable master data (name, cost, etc.)
- **Consistency**: Database transactions ensure atomic writes

### Two-Table Pattern Details

**Write Path (Command):**
```
User Action → Validation → INSERT movement → [optional UPDATE item] → COMMIT
```

**Read Path (Query):**
```
Dashboard Request → Query current_stock view → Aggregate movements → Return computed state
```

This achieves:
- ✅ Complete audit trail (every operation recorded)
- ✅ Time-travel queries possible (recompute stock at any point in time)
- ✅ Immutability (movements never edited/deleted)
- ✅ Simple to implement (no complex event replay, just SQL aggregation)

### Optimistic Locking Strategy

For this single-user application, **optimistic locking is not strictly required**, but can be added if multi-user support is needed later:

**Version-based approach (future enhancement):**

```sql
-- Add version column to items
ALTER TABLE items ADD COLUMN version INTEGER NOT NULL DEFAULT 1;

-- On update, check version hasn't changed
UPDATE items
SET name = ?, version = version + 1
WHERE id = ? AND version = ?;

-- If rowcount = 0, someone else updated → conflict
```

**For this MVP:** Race conditions are unlikely (single user, low concurrency). Use database transactions as sufficient protection.

### Concurrency Handling

**Scenario:** User has multiple browser tabs open, tries to register movements simultaneously.

**Solution:**
1. **Database transaction isolation**: Use `READ COMMITTED` or higher
2. **Row-level locking**: PostgreSQL handles concurrent INSERTs to movements automatically
3. **Validation at transaction time**: Check current_stock inside transaction before INSERT OUT
4. **Retry logic**: If transaction fails (rare), show user-friendly error and ask to retry

**Example transaction (Python pseudocode):**
```python
with db.begin():  # Start transaction
    # Lock-free: current_stock view recomputes inside transaction
    current = db.execute(
        select(func.sum(Movement.quantity))
        .where(Movement.item_id == item_id)
    ).scalar() or 0

    new_stock = current + quantity
    if new_stock < 0:
        raise ValueError("Giacenza insufficiente")

    # Insert movement (append-only, no locking needed)
    movement = Movement(item_id=item_id, quantity=quantity, ...)
    db.add(movement)

    # COMMIT (automatic on context exit)
```

**Edge case - simultaneous OUT movements:**
- User A and B both see current_stock = 10
- User A tries to OUT -8 (should leave 2)
- User B tries to OUT -5 (should leave 5)
- Both should succeed? No! Second transaction will see updated stock inside its own transaction.

PostgreSQL's MVCC ensures each transaction sees consistent snapshot. The second transaction will see stock = 2 (after A's commit) and correctly block B's attempt to OUT -5.

### Time-Travel Queries (Bonus Feature)

The event-sourced design enables querying historical stock at any point in time:

```sql
-- Stock on specific date
SELECT
    i.name,
    COALESCE(SUM(m.quantity), 0) AS stock_on_date
FROM items i
LEFT JOIN movements m ON m.item_id = i.id
    AND m.movement_date <= '2024-12-31'
GROUP BY i.id, i.name;

-- Stock changes between two dates
SELECT
    i.name,
    SUM(CASE WHEN m.movement_date <= '2024-01-01' THEN m.quantity ELSE 0 END) AS stock_start,
    SUM(CASE WHEN m.movement_date <= '2024-12-31' THEN m.quantity ELSE 0 END) AS stock_end,
    SUM(CASE WHEN m.movement_date BETWEEN '2024-01-01' AND '2024-12-31'
             THEN m.quantity ELSE 0 END) AS net_change
FROM items i
LEFT JOIN movements m ON m.item_id = i.id
GROUP BY i.id, i.name;
```

Not required for MVP but demonstrates architectural benefit.

### Version Handling

**Current approach:** No explicit versioning. Items are mutable (name, cost, etc. can change), movements are immutable.

**Future enhancement (if needed):**
- Add `items.version` column
- On every update, increment version
- Store `movement.item_version` to know which item state was active during that movement
- Enables reconstructing exact historical context (e.g., "What was the unit cost when this IN movement occurred?")

For now, this is over-engineering. The spec doesn't require it.

---

## Data Integrity Rules

### Invariants (Always True)

1. **Stock non-negativity**: `∀ items: SUM(movements.quantity WHERE item_id = items.id) >= 0`
   - Enforced by application validation before INSERT OUT/ADJUSTMENT

2. **Movement immutability**: Once inserted, movements are never UPDATEd or DELETEd
   - Enforced by application (no update/delete endpoints)
   - Database-level: Revoke UPDATE/DELETE permissions on movements table

3. **Referential integrity**: `∀ movements: EXISTS(item WHERE item.id = movement.item_id)`
   - Enforced by FOREIGN KEY constraint with ON DELETE RESTRICT

4. **Type-quantity consistency**:
   - `movement_type = 'IN' → quantity > 0`
   - `movement_type = 'OUT' → quantity < 0`
   - `movement_type = 'ADJUSTMENT' → quantity ≠ 0`
   - Enforced by CHECK constraints

5. **ADJUSTMENT note requirement**: `movement_type = 'ADJUSTMENT' → note IS NOT NULL AND LENGTH(note) > 0`
   - Enforced by application validation (cannot be done in CHECK constraint across columns reliably)

6. **Cost override restriction**: `unit_cost_override IS NOT NULL → movement_type = 'IN'`
   - Enforced by CHECK constraint

### Transaction Boundaries

**Atomic operations:**

1. **Register IN movement + update cost:**
   ```sql
   BEGIN;
       INSERT INTO movements (...) VALUES (...);
       UPDATE items SET unit_cost = ? WHERE id = ?;  -- if override provided
   COMMIT;
   ```

2. **Register OUT movement with validation:**
   ```sql
   BEGIN;
       -- Read current stock (inside transaction for consistency)
       SELECT COALESCE(SUM(quantity), 0) INTO current_stock
       FROM movements WHERE item_id = ?;

       -- Validate (application layer)
       IF current_stock + new_quantity < 0 THEN
           RAISE EXCEPTION 'Giacenza insufficiente';
       END IF;

       -- Insert movement
       INSERT INTO movements (...) VALUES (...);
   COMMIT;
   ```

3. **Register ADJUSTMENT movement:**
   ```sql
   BEGIN;
       -- Read current stock
       SELECT COALESCE(SUM(quantity), 0) INTO current_stock
       FROM movements WHERE item_id = ?;

       -- Calculate delta
       adjustment_quantity := target_stock - current_stock;

       -- Validate
       IF adjustment_quantity = 0 THEN
           RAISE EXCEPTION 'Nessuna rettifica necessaria';
       END IF;
       IF target_stock < 0 THEN
           RAISE EXCEPTION 'Giacenza target non può essere negativa';
       END IF;
       IF note IS NULL OR LENGTH(TRIM(note)) = 0 THEN
           RAISE EXCEPTION 'Nota obbligatoria per rettifiche';
       END IF;

       -- Insert movement
       INSERT INTO movements (quantity = adjustment_quantity, ...) VALUES (...);
   COMMIT;
   ```

4. **Delete item with checks:**
   ```sql
   BEGIN;
       -- Check current stock
       SELECT COALESCE(SUM(quantity), 0) INTO stock
       FROM movements WHERE item_id = ?;
       IF stock > 0 THEN
           RAISE EXCEPTION 'Giacenza non zero';
       END IF;

       -- Check recent movements
       SELECT COUNT(*) INTO recent_count
       FROM movements
       WHERE item_id = ? AND movement_date >= CURRENT_DATE - INTERVAL '12 months';
       IF recent_count > 0 THEN
           RAISE EXCEPTION 'Movimenti recenti esistenti';
       END IF;

       -- Delete (movements preserved by RESTRICT constraint)
       DELETE FROM items WHERE id = ?;
   COMMIT;
   ```

### Backup and Recovery

**Recommendation:**
- **Daily backups**: Automated PostgreSQL dumps
- **Point-in-time recovery**: Enable WAL archiving
- **Export as backup**: FR-025 Excel export can serve as human-readable backup

Event-sourced architecture provides natural disaster recovery: if `current_stock` view is corrupted, it can be reconstructed from `movements` at any time.

---

## SQLAlchemy 2.x Models (Reference)

Below are example SQLAlchemy model definitions implementing this schema:

```python
from sqlalchemy import (
    Column, String, Text, Numeric, DateTime, Date,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class Item(Base):
    __tablename__ = 'items'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    unit = Column(String(20), nullable=False, default='pz')
    notes = Column(Text)
    min_stock = Column(Numeric(10, 3), nullable=False, default=0)
    unit_cost = Column(Numeric(10, 2), nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    movements = relationship('Movement', back_populates='item', cascade='all, delete-orphan')

    # Constraints
    __table_args__ = (
        CheckConstraint('LENGTH(TRIM(name)) > 0', name='chk_items_name_not_empty'),
        CheckConstraint('min_stock >= 0', name='chk_items_min_stock_positive'),
        CheckConstraint('unit_cost >= 0', name='chk_items_unit_cost_positive'),
        CheckConstraint('LENGTH(TRIM(unit)) > 0', name='chk_items_unit_not_empty'),
        Index('idx_items_name_trgm', 'name', postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'}),
        Index('idx_items_category', 'category'),
        Index('idx_items_created_at', 'created_at'),
    )


class Movement(Base):
    __tablename__ = 'movements'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = Column(UUID(as_uuid=True), ForeignKey('items.id', ondelete='RESTRICT'), nullable=False)
    movement_type = Column(String(20), nullable=False)
    quantity = Column(Numeric(10, 3), nullable=False)
    movement_date = Column(Date, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    unit_cost_override = Column(Numeric(10, 2))
    note = Column(Text)
    created_by = Column(String(100))

    # Relationships
    item = relationship('Item', back_populates='movements')

    # Constraints
    __table_args__ = (
        CheckConstraint("movement_type IN ('IN', 'OUT', 'ADJUSTMENT')", name='chk_movements_type_valid'),
        CheckConstraint('quantity != 0', name='chk_movements_quantity_nonzero'),
        CheckConstraint('unit_cost_override IS NULL OR unit_cost_override >= 0', name='chk_movements_cost_positive'),
        CheckConstraint("movement_type != 'IN' OR quantity > 0", name='chk_movements_in_positive'),
        CheckConstraint("movement_type != 'OUT' OR quantity < 0", name='chk_movements_out_negative'),
        CheckConstraint("unit_cost_override IS NULL OR movement_type = 'IN'", name='chk_movements_cost_in_only'),
        Index('idx_movements_item_id', 'item_id'),
        Index('idx_movements_timestamp', 'timestamp'),
        Index('idx_movements_movement_date', 'movement_date'),
        Index('idx_movements_type', 'movement_type'),
        Index('idx_movements_item_date', 'item_id', 'movement_date'),
    )
```

**View query (not a model, but used in queries):**

```python
from sqlalchemy import select, func, case

current_stock_query = (
    select(
        Item.id.label('item_id'),
        Item.name.label('item_name'),
        Item.category,
        Item.unit,
        Item.min_stock,
        Item.unit_cost,
        Item.notes,
        func.coalesce(func.sum(Movement.quantity), 0).label('stock_quantity'),
        (func.coalesce(func.sum(Movement.quantity), 0) * Item.unit_cost).label('stock_value'),
        case(
            (func.coalesce(func.sum(Movement.quantity), 0) < Item.min_stock, True),
            else_=False
        ).label('is_under_min_stock'),
        func.max(Movement.timestamp).label('last_movement_at')
    )
    .select_from(Item)
    .outerjoin(Movement, Movement.item_id == Item.id)
    .group_by(Item.id, Item.name, Item.category, Item.unit, Item.min_stock, Item.unit_cost, Item.notes)
)

# Usage:
result = session.execute(current_stock_query).all()
```

---

## Migration Strategy

### Initial Schema Setup

**Order of operations:**

1. Enable extensions:
   ```sql
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For trigram indexes
   ```

2. Create `items` table with constraints and indexes

3. Create `movements` table with constraints, indexes, and foreign key

4. Create `current_stock` view

5. Grant appropriate permissions (if using restricted database user)

### Sample Data (Testing)

```sql
-- Insert sample items
INSERT INTO items (id, name, category, unit, min_stock, unit_cost, notes) VALUES
    (gen_random_uuid(), 'Olio motore 5W30', 'Lubrificanti', 'lt', 5, 8.50, 'Olio sintetico long life'),
    (gen_random_uuid(), 'Filtro olio', 'Filtri', 'pz', 10, 4.20, 'Compatibile maggior parte veicoli'),
    (gen_random_uuid(), 'Pastiglie freno anteriori', 'Freni', 'kit', 3, 35.00, 'Set completo asse anteriore'),
    (gen_random_uuid(), 'Liquido freni DOT4', 'Liquidi', 'lt', 2, 6.80, 'Specifica DOT4 - 1 litro');

-- Insert sample movements (adjust item_id to match generated UUIDs)
INSERT INTO movements (item_id, movement_type, quantity, movement_date, note) VALUES
    ((SELECT id FROM items WHERE name = 'Olio motore 5W30'), 'IN', 20, CURRENT_DATE - INTERVAL '30 days', 'Carico iniziale magazzino'),
    ((SELECT id FROM items WHERE name = 'Olio motore 5W30'), 'OUT', -3, CURRENT_DATE - INTERVAL '15 days', 'Tagliando Alfa Romeo 159'),
    ((SELECT id FROM items WHERE name = 'Filtro olio'), 'IN', 25, CURRENT_DATE - INTERVAL '60 days', 'Fornitore A - Fattura 123'),
    ((SELECT id FROM items WHERE name = 'Filtro olio'), 'OUT', -18, CURRENT_DATE - INTERVAL '10 days', 'Utilizzo misto officina'),
    ((SELECT id FROM items WHERE name = 'Filtro olio'), 'ADJUSTMENT', -2, CURRENT_DATE - INTERVAL '5 days', 'Conteggio fisico: 2 unità danneggiate');

-- Verify current stock
SELECT * FROM current_stock ORDER BY is_under_min_stock DESC, item_name;
```

---

## Appendix: Requirement Traceability

| Requirement | Database Element | Implementation |
|-------------|------------------|----------------|
| FR-001 | `current_stock` view | Real-time aggregation of movements |
| FR-002 | `idx_items_name_trgm` | GIN trigram index for partial matching |
| FR-003 | `idx_items_category` | B-tree index for category filtering |
| FR-004 | `current_stock.is_under_min_stock` | Computed boolean flag |
| FR-005 | Application layer | Visual styling based on `is_under_min_stock` |
| FR-006 | `movements` table | `movement_type='IN'`, positive quantity |
| FR-007 | `movements` table | `movement_type='OUT'`, negative quantity |
| FR-008 | Application validation | Pre-insert stock check for OUT movements |
| FR-009 | Application layer | Confirmation dialog before OUT insert |
| FR-010 | Trigger/app logic | Update `items.unit_cost` after IN with override |
| FR-011 | `movements.timestamp` | Server-side `DEFAULT CURRENT_TIMESTAMP` |
| FR-012 | Database transactions | Atomic INSERT/UPDATE in single transaction |
| FR-013 | `items` table | CREATE operation with default values |
| FR-014 | `items` table | UPDATE operation (stock read-only) |
| FR-015 | Application validation | Pre-delete checks (stock=0, no recent movements) |
| FR-016 | Application validation | Block delete if `current_stock > 0` |
| FR-017 | Application validation | Block delete if movements exist <12 months |
| FR-018 | Application query | `SELECT DISTINCT category/unit FROM items` |
| FR-019 | `chk_movements_quantity_nonzero` | CHECK constraint |
| FR-020 | `chk_items_name_not_empty` | CHECK constraint |
| FR-021 | `NUMERIC` types + CHECK | Data type + non-negative constraints |
| FR-022 | `idx_movements_movement_date` | Date range filtering with index |
| FR-023 | `movements` columns | All required fields stored |
| FR-024 | `idx_movements_timestamp` | DESC index for reverse chronological order |
| FR-025-029 | Application layer | Excel export logic (not database) |
| FR-036 | `movements` table | `movement_type='ADJUSTMENT'` |
| FR-037 | Application logic | Calculate delta: `target - current` |
| FR-038 | Application validation | Block if delta = 0 |
| FR-039 | Application validation | Enforce non-empty note for ADJUSTMENT |
| FR-040 | Application display | Show sign (+/-) in UI for ADJUSTMENT |
| FR-041 | `current_stock.stock_value` | Computed `quantity * unit_cost` |
| FR-042 | Application query | `COUNT(*) WHERE is_under_min_stock = TRUE` |

---

## Document Metadata

**Version**: 1.0
**Last Updated**: 2025-11-11
**Author**: System Architect
**Review Status**: Draft
**Related Documents**:
- Feature Specification: `spec.md`
- Implementation Plan: `plan.md` (to be created)
- API Documentation: `api.md` (to be created)

**Database Schema Version**: `001-initial-schema`
**Migration Scripts**: `/migrations/001_initial_schema.sql` (to be created)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-11 | System | Initial data model specification based on feature spec |

---

**End of Data Model Document**
