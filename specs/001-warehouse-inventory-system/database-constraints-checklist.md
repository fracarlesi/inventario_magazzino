# Database Constraints Verification Checklist

**Purpose**: Validate that Alembic migration 001_initial_schema.py (T009-T010) includes all required database constraints for data integrity per Constitution Principle II.

**Migration File**: `backend/alembic/versions/001_initial_schema.py`

---

## Items Table Constraints

Verify these constraints exist in the `items` table creation:

- [ ] **chk_items_name_not_empty**: Name field validation
  ```sql
  ALTER TABLE items ADD CONSTRAINT chk_items_name_not_empty
    CHECK (name IS NOT NULL AND LENGTH(TRIM(name)) > 0);
  ```
  **Maps to**: FR-020 (name non-empty validation)

- [ ] **chk_items_min_stock_positive**: Minimum stock non-negative
  ```sql
  ALTER TABLE items ADD CONSTRAINT chk_items_min_stock_positive
    CHECK (min_stock >= 0);
  ```
  **Maps to**: FR-013 (min_stock default 0, must be >= 0)

- [ ] **chk_items_unit_cost_positive**: Unit cost non-negative
  ```sql
  ALTER TABLE items ADD CONSTRAINT chk_items_unit_cost_positive
    CHECK (unit_cost >= 0);
  ```
  **Maps to**: FR-013 (unit_cost default 0, must be >= 0), allows zero-cost items

- [ ] **pk_items**: Primary key on UUID id
  ```sql
  PRIMARY KEY (id)
  ```

- [ ] **items_name_unique**: Optional unique constraint if enforcing no duplicates
  ```sql
  -- OPTIONAL: Consider if item names should be globally unique
  -- ALTER TABLE items ADD CONSTRAINT items_name_unique UNIQUE (name);
  ```
  **Decision**: NOT REQUIRED per spec (same item name allowed, differentiated by id)

---

## Movements Table Constraints

Verify these constraints exist in the `movements` table creation:

- [ ] **chk_movements_quantity_nonzero**: Quantity cannot be zero
  ```sql
  ALTER TABLE movements ADD CONSTRAINT chk_movements_quantity_nonzero
    CHECK (quantity != 0);
  ```
  **Maps to**: FR-019 (quantity > 0), allows negative for OUT movements

- [ ] **chk_movements_type_valid**: Movement type enum validation
  ```sql
  ALTER TABLE movements ADD CONSTRAINT chk_movements_type_valid
    CHECK (movement_type IN ('IN', 'OUT', 'ADJUSTMENT'));
  ```
  **Maps to**: Key Entities (movement_type enum), FR-006, FR-007, FR-036

- [ ] **chk_movements_in_positive**: IN movements must have positive quantity
  ```sql
  ALTER TABLE movements ADD CONSTRAINT chk_movements_in_positive
    CHECK (movement_type != 'IN' OR quantity > 0);
  ```
  **Maps to**: FR-006 (IN quantity > 0)

- [ ] **chk_movements_out_negative**: OUT movements must have negative quantity
  ```sql
  ALTER TABLE movements ADD CONSTRAINT chk_movements_out_negative
    CHECK (movement_type != 'OUT' OR quantity < 0);
  ```
  **Maps to**: FR-007 (OUT quantity converted to negative)

- [ ] **chk_movements_adjustment_note**: ADJUSTMENT movements require mandatory note
  ```sql
  ALTER TABLE movements ADD CONSTRAINT chk_movements_adjustment_note
    CHECK (movement_type != 'ADJUSTMENT' OR (note IS NOT NULL AND LENGTH(TRIM(note)) > 0));
  ```
  **Maps to**: FR-039 (ADJUSTMENT note mandatory)

- [ ] **fk_movements_item_id**: Foreign key to items table
  ```sql
  ALTER TABLE movements ADD CONSTRAINT fk_movements_item_id
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE RESTRICT;
  ```
  **Maps to**: Key Entities (movement references item), prevents orphaned movements

- [ ] **pk_movements**: Primary key on UUID id
  ```sql
  PRIMARY KEY (id)
  ```

---

## Indexes (Performance)

Verify these indexes exist for query optimization:

- [ ] **idx_items_name_trgm**: Trigram index for partial name search
  ```sql
  CREATE INDEX idx_items_name_trgm ON items USING gin (name gin_trgm_ops);
  ```
  **Maps to**: FR-002 (name search optimization), requires `pg_trgm` extension

- [ ] **idx_items_category**: Category filter optimization
  ```sql
  CREATE INDEX idx_items_category ON items (category);
  ```
  **Maps to**: FR-003 (category filter)

- [ ] **idx_movements_item_id**: Movement lookup by item
  ```sql
  CREATE INDEX idx_movements_item_id ON movements (item_id);
  ```
  **Maps to**: Stock calculation queries, movement history per item

- [ ] **idx_movements_timestamp**: Movement ordering by timestamp
  ```sql
  CREATE INDEX idx_movements_timestamp ON movements (timestamp DESC);
  ```
  **Maps to**: FR-024 (movements ordered DESC by date)

- [ ] **idx_movements_movement_date**: Movement filtering by date range
  ```sql
  CREATE INDEX idx_movements_movement_date ON movements (movement_date);
  ```
  **Maps to**: FR-022 (date range filter), FR-028 (12-month export filter)

- [ ] **idx_movements_type**: Movement filtering by type
  ```sql
  CREATE INDEX idx_movements_type ON movements (movement_type);
  ```
  **Maps to**: FR-022 (type filter: IN/OUT/ADJUSTMENT/All)

---

## PostgreSQL Extensions

Verify these extensions are enabled before table creation:

- [ ] **uuid-ossp**: UUID generation
  ```sql
  CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
  ```
  **Required for**: UUID primary keys on items and movements tables

- [ ] **pg_trgm**: Trigram text search
  ```sql
  CREATE EXTENSION IF NOT EXISTS pg_trgm;
  ```
  **Required for**: idx_items_name_trgm index (FR-002 name search)

---

## Current Stock View

Verify the materialized or regular view exists:

- [ ] **current_stock view**: Aggregates movements to compute stock
  ```sql
  CREATE VIEW current_stock AS
  SELECT
    i.id AS item_id,
    i.name,
    i.category,
    i.unit,
    i.min_stock,
    i.unit_cost,
    COALESCE(SUM(m.quantity), 0) AS stock_quantity,
    COALESCE(SUM(m.quantity), 0) * i.unit_cost AS stock_value,
    (COALESCE(SUM(m.quantity), 0) < i.min_stock) AS is_under_min_stock,
    MAX(m.timestamp) AS last_movement_at
  FROM items i
  LEFT JOIN movements m ON m.item_id = i.id
  GROUP BY i.id, i.name, i.category, i.unit, i.min_stock, i.unit_cost;
  ```
  **Maps to**: FR-001 (real-time stock computation), FR-004 (under-stock detection)

- [ ] **Optional: Materialized view with refresh strategy**
  ```sql
  -- Alternative for performance with large datasets:
  -- CREATE MATERIALIZED VIEW current_stock AS [...];
  -- REFRESH MATERIALIZED VIEW current_stock; -- Called after mutations
  ```
  **Decision**: Use regular VIEW for MVP (real-time), consider MATERIALIZED if >10K movements causes slowness

---

## Validation Commands

Run these SQL queries after migration to verify constraints:

```sql
-- List all constraints on items table
SELECT conname, contype, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'items'::regclass;

-- List all constraints on movements table
SELECT conname, contype, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'movements'::regclass;

-- List all indexes on items table
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'items';

-- List all indexes on movements table
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'movements';

-- Verify extensions enabled
SELECT * FROM pg_extension WHERE extname IN ('uuid-ossp', 'pg_trgm');

-- Test current_stock view
SELECT * FROM current_stock LIMIT 5;
```

---

## Test Cases for Constraint Validation

After migration, run these INSERT tests to verify constraints block invalid data:

### Test FR-020: Name NOT NULL/Empty
```sql
-- Should FAIL
INSERT INTO items (id, name, unit, min_stock, unit_cost)
VALUES (uuid_generate_v4(), '', 'pz', 0, 0);
-- Expected: ERROR: check constraint "chk_items_name_not_empty" violated
```

### Test FR-019: Quantity Non-Zero
```sql
-- Should FAIL
INSERT INTO movements (id, item_id, movement_type, quantity, movement_date, timestamp)
VALUES (uuid_generate_v4(), '<valid_item_id>', 'IN', 0, CURRENT_DATE, NOW());
-- Expected: ERROR: check constraint "chk_movements_quantity_nonzero" violated
```

### Test FR-006: IN Positive Quantity
```sql
-- Should FAIL
INSERT INTO movements (id, item_id, movement_type, quantity, movement_date, timestamp)
VALUES (uuid_generate_v4(), '<valid_item_id>', 'IN', -5, CURRENT_DATE, NOW());
-- Expected: ERROR: check constraint "chk_movements_in_positive" violated
```

### Test FR-007: OUT Negative Quantity
```sql
-- Should FAIL
INSERT INTO movements (id, item_id, movement_type, quantity, movement_date, timestamp)
VALUES (uuid_generate_v4(), '<valid_item_id>', 'OUT', 5, CURRENT_DATE, NOW());
-- Expected: ERROR: check constraint "chk_movements_out_negative" violated
```

### Test FR-039: ADJUSTMENT Mandatory Note
```sql
-- Should FAIL
INSERT INTO movements (id, item_id, movement_type, quantity, movement_date, timestamp, note)
VALUES (uuid_generate_v4(), '<valid_item_id>', 'ADJUSTMENT', 3, CURRENT_DATE, NOW(), NULL);
-- Expected: ERROR: check constraint "chk_movements_adjustment_note" violated
```

---

## Sign-Off

After verifying all checkboxes above:

- [ ] **Migration T009-T010 Complete**: All constraints and indexes created
- [ ] **Validation SQL Passed**: Queries return expected constraints
- [ ] **Test Cases Passed**: Invalid data correctly blocked by constraints
- [ ] **Extensions Enabled**: uuid-ossp and pg_trgm confirmed active
- [ ] **Current Stock View Working**: Query returns computed stock values

**Verified By**: _______________
**Date**: _______________
**Migration Version**: 001_initial_schema
**Database**: (Local PostgreSQL / Neon Production)

---

## References

- **spec.md**: FR-001 to FR-045 (functional requirements)
- **data-model.md**: Complete schema definition with constraint details
- **tasks.md**: T009-T012 (migration tasks)
- **constitution.md**: Principle II (Data Integrity - NON-NEGOTIABLE)
- **plan.md**: Post-design Constitution Check validation

**Next Step After Verification**: Proceed to Phase 2 foundational tasks (T013-T018) to build models and services on validated schema.
