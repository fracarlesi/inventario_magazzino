# Tasks: Sistema di Gestione Magazzino Officina

**Feature Branch**: `001-warehouse-inventory-system`
**Date**: 2025-11-11
**Input**: Design documents from `/Users/francescocarlesi/Downloads/Progetti Python/inventario_magazzino/specs/001-warehouse-inventory-system/`

**Prerequisites**:
- [spec.md](./spec.md) - 7 user stories (US1-P1, US2-P2, US3-P3, US4-P4, US7-P4, US5-P5, US6-P6)
- [plan.md](./plan.md) - Tech stack (FastAPI, SQLAlchemy, Next.js, PostgreSQL, Neon, Render, Vercel)
- [data-model.md](./data-model.md) - Entities (items, movements, current_stock view)
- [contracts/openapi.yaml](./contracts/openapi.yaml) - 12 API endpoints
- [research.md](./research.md) - Deployment decisions

---

## Summary

**Total Tasks**: 102 (98 original + 4 remediation tasks: T008.1, T032.1, T083.1, T083.2)
**User Stories**: 7 (US1-P1 MVP, US2-P2, US3-P3, US4-P4, US7-P4, US5-P5, US6-P6)
**Test Tasks**: 0 (tests not requested in spec)

**Task Distribution by Phase**:
- Phase 1 (Setup): 6 tasks
- Phase 2 (Foundational): 13 tasks (includes T008.1 CRITICAL - Neon pooling)
- Phase 3 (US1 - Dashboard): 15 tasks (includes T032.1 keyboard navigation)
- Phase 4 (US2 - IN movements): 8 tasks
- Phase 5 (US3 - OUT movements): 8 tasks
- Phase 6 (US4 - Items CRUD): 11 tasks
- Phase 7 (US7 - ADJUSTMENT): 8 tasks
- Phase 8 (US5 - Movement history): 7 tasks
- Phase 9 (US6 - Excel export): 6 tasks
- Phase 10 (Polish & Deployment): 20 tasks (includes T083.1 validation, T083.2 locale checklist, T086 deprecated)

---

## Format: `- [ ] T### [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story tag (US1, US2, US3, US4, US5, US6, US7)
- All file paths are absolute or relative to repository root

---

## Implementation Strategy

### MVP First (US1 Only)
1. Complete Phase 1 (Setup)
2. Complete Phase 2 (Foundational) - CRITICAL BLOCKER
3. Complete Phase 3 (US1 - Dashboard) - MVP!
4. VALIDATE: Test independently, deploy

### Incremental Delivery (Priority Order)
1. Setup + Foundational → Foundation ready
2. US1 (P1) → Dashboard inventory view → MVP deployed
3. US2 (P2) → Register IN movements → Feature complete
4. US3 (P3) → Register OUT movements → Feature complete
5. US4 (P4) → Manage items CRUD → Feature complete
6. US7 (P4) → Inventory ADJUSTMENT → Feature complete
7. US5 (P5) → Movement history → Feature complete
8. US6 (P6) → Excel export → All stories complete
9. Polish & Deployment → Production ready

---

## Dependency Graph

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKS ALL USER STORIES
    ↓
    ├─→ Phase 3 (US1 - P1 MVP) ← Can start independently
    ├─→ Phase 4 (US2 - P2)     ← Can start independently
    ├─→ Phase 5 (US3 - P3)     ← Can start independently
    ├─→ Phase 6 (US4 - P4)     ← Can start independently
    ├─→ Phase 7 (US7 - P4)     ← Can start independently
    ├─→ Phase 8 (US5 - P5)     ← Can start independently
    └─→ Phase 9 (US6 - P6)     ← Can start independently
         ↓
Phase 10 (Polish & Deployment)
```

**Parallel Execution**: All user story phases (3-9) can run in parallel once Phase 2 completes.

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize project structure and dependencies

**Duration**: ~2 hours

- [X] T001 [P] Create backend directory structure: `backend/src/{models,services,api,db}`, `backend/tests/{unit,integration}`
- [X] T002 [P] Create frontend directory structure: `frontend/src/{components,pages,services,types,i18n}`, `frontend/tests/{unit,e2e}`
- [X] T003 Initialize Python 3.11+ project in `backend/` with pyproject.toml and requirements.txt (FastAPI, SQLAlchemy 2.x, Alembic, psycopg2-binary, pydantic, pytest)
- [X] T004 Initialize Next.js 14+ TypeScript project in `frontend/` with package.json (React, TypeScript 5.x, xlsx/SheetJS, SWR, TailwindCSS, react-number-format, @tanstack/react-table, next-i18next)
- [X] T005 [P] Configure ESLint, Prettier in `frontend/` and Black, Flake8 in `backend/`
- [X] T006 [P] Create .gitignore files for Python (venv, __pycache__, .env) and Node.js (node_modules, .next, .env.local)

**Checkpoint**: Project structure ready, dependencies installable

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

**Duration**: ~6 hours

### Database & Migrations

- [X] T007 Setup PostgreSQL connection in `backend/src/db/database.py` with SQLAlchemy engine and session management
- [X] T008 Initialize Alembic in `backend/alembic/` with env.py configured for SQLAlchemy 2.x models
- [X] T008.1 [P] [CRITICAL] Configure database.py to use Neon pooled endpoint (URL must contain `.pooler.neon.tech` not direct `.neon.tech`) with `poolclass=NullPool` in SQLAlchemy engine to prevent connection exhaustion on serverless deployment. Document in env.example: `DATABASE_URL=postgresql://user:pass@ep-xxx.pooler.neon.tech:5432/dbname?sslmode=require`
- [X] T009 Create initial migration `backend/alembic/versions/001_initial_schema.py`: items table (id, name, category, unit, notes, min_stock, unit_cost, created_at, updated_at) with CHECK constraints
- [X] T010 Extend migration 001: movements table (id, item_id, movement_type, quantity, movement_date, timestamp, unit_cost_override, note, created_by) with FK to items and CHECK constraints
- [X] T011 Extend migration 001: Enable PostgreSQL extensions (uuid-ossp, pg_trgm) and create indexes (idx_items_name_trgm, idx_items_category, idx_movements_item_id, idx_movements_timestamp, idx_movements_movement_date, idx_movements_type)
- [X] T012 Create current_stock database view in migration 001: aggregate movements by item_id with stock_quantity, stock_value, is_under_min_stock, last_movement_at

### Backend Core Models

- [X] T013 [P] Create Item SQLAlchemy model in `backend/src/models/item.py` with validation (name NOT NULL, min_stock >= 0, unit_cost >= 0)
- [X] T014 [P] Create Movement SQLAlchemy model in `backend/src/models/movement.py` with CHECK constraints (movement_type IN ['IN','OUT','ADJUSTMENT'], quantity != 0, IN positive, OUT negative)
- [X] T015 Create Pydantic schemas in `backend/src/models/schemas.py`: ItemCreate, ItemUpdate, ItemWithStock, MovementInCreate, MovementOutCreate, MovementAdjustmentCreate, MovementDetail, ErrorResponse

### Backend API Infrastructure

- [X] T016 Setup FastAPI app in `backend/src/main.py` with CORS middleware (allow origins from env), exception handlers, and API router registration
- [X] T017 Create database dependency in `backend/src/db/database.py`: get_db() session factory for FastAPI dependency injection
- [X] T018 [P] Create error handling utilities in `backend/src/api/errors.py`: custom exceptions (ItemNotFound, InsufficientStock, ValidationError) with Italian error messages

**Checkpoint**: Foundation ready - database migrated, models defined, FastAPI running on http://localhost:8000

---

## Phase 3: User Story 1 - Visualizzare e Cercare Inventario Corrente (Priority: P1) 🎯 MVP

**Goal**: Dashboard shows real-time inventory with filters (name search, category, under-stock toggle) and statistics

**Independent Test Criteria**:
1. Open http://localhost:3000 → see dashboard with item table
2. Search "bullone" → table filters by name
3. Select category "Filtri olio" → table filters by category
4. Toggle "solo sotto scorta" → shows only items with stock < min_stock
5. Items with stock < min_stock display visual warning

**User Stories Mapped**: US1 (FR-001, FR-002, FR-003, FR-004, FR-005, FR-041, FR-042)

**API Endpoints Required**:
- GET /api/items (with filters: search, category, under_stock_only, sort_by, sort_order)
- GET /api/dashboard/stats

**Duration**: ~8 hours

### Backend Implementation

- [X] T019 [P] [US1] Implement GET /api/items endpoint in `backend/src/api/items.py`: query current_stock view with filters (search via ILIKE, category exact match, under_stock_only boolean, sort_by, sort_order), return ItemWithStock array
- [X] T020 [US1] Implement current_stock query service in `backend/src/services/stock_service.py`: aggregate movements by item_id with COALESCE for zero-movement items, compute stock_quantity, stock_value, is_under_min_stock
- [X] T021 [P] [US1] Implement GET /api/dashboard/stats endpoint in `backend/src/api/dashboard.py`: calculate total_warehouse_value (SUM stock_value), under_stock_count (COUNT WHERE is_under_min_stock), total_items_count, zero_stock_count
- [X] T022 [US1] Add name search optimization in `backend/src/services/stock_service.py`: use pg_trgm GIN index for partial case-insensitive matching (idx_items_name_trgm)
- [X] T023 [US1] Add validation in `backend/src/api/items.py`: validate sort_by enum (name, category, stock_quantity, is_under_min_stock), sort_order enum (asc, desc), return 400 with Italian error message if invalid

### Frontend Implementation

- [X] T024 [P] [US1] Create ItemTable component in `frontend/src/components/ItemTable.tsx` using @tanstack/react-table: display items with columns (name, category, unit, stock_quantity, min_stock, unit_cost, stock_value, is_under_min_stock), highlight under-stock rows. Use react-table for ARIA-compliant markup (<th scope="col">, role="row", role="cell"), built-in keyboard navigation support, and screen reader accessibility per FR-034
- [X] T025 [P] [US1] Create SearchBar component in `frontend/src/components/SearchBar.tsx`: debounced text input for name search
- [X] T026 [P] [US1] Create CategoryFilter component in `frontend/src/components/CategoryFilter.tsx`: dropdown select with "Tutte le categorie" option
- [X] T027 [P] [US1] Create UnderStockToggle component in `frontend/src/components/UnderStockToggle.tsx`: checkbox toggle for "solo sotto scorta" filter
- [X] T028 [P] [US1] Create DashboardStats component in `frontend/src/components/DashboardStats.tsx`: display total_warehouse_value (EUR formatted), under_stock_count, total_items_count, zero_stock_count
- [X] T029 [US1] Create Dashboard page in `frontend/src/pages/index.tsx`: integrate ItemTable, SearchBar, CategoryFilter, UnderStockToggle, DashboardStats with SWR for data fetching from /api/items and /api/dashboard/stats
- [X] T030 [US1] Implement API client in `frontend/src/services/api.ts`: fetchItems(filters), fetchDashboardStats() with axios, handle errors and return Italian error messages
- [X] T031 [US1] Add Italian i18n strings in `frontend/src/i18n/it.json`: dashboard labels (Nome, Categoria, Giacenza, Sotto Scorta, etc.), search placeholder, filter labels
- [X] T032 [US1] Add visual styling in `frontend/src/components/ItemTable.tsx`: red background for is_under_min_stock rows, EUR currency formatting for costs/values, number formatting for quantities (2 decimals)
- [X] T032.1 [P] [US1] Add keyboard navigation to Dashboard in `frontend/src/pages/index.tsx` and components: Tab order for all interactive elements (search input, category filter, under-stock toggle, table rows via @tanstack/react-table built-in support), Enter to submit forms, Escape to close modals/dialogs, visible focus indicators (outline: 2px solid blue on :focus-visible) per FR-034. React-table provides ARIA navigation patterns out-of-the-box.

**Checkpoint**: MVP complete - dashboard displays inventory, filters work, under-stock items highlighted, statistics shown, keyboard accessible

---

## Phase 4: User Story 2 - Registrare Carico Merce (IN) (Priority: P2)

**Goal**: User can register IN movements, optionally override unit cost, system updates stock and item cost

**Independent Test Criteria**:
1. Click "Carico (IN)" button → form opens
2. Select article "Olio motore 5W30" with current stock 10
3. Enter quantity 20, date (default today), note "Fornitore A", cost override €5.50
4. Submit → movement saved, stock becomes 30, item unit_cost updated to €5.50
5. Verify quantity validation: entering 0 or negative shows error "La quantità deve essere maggiore di zero"

**User Stories Mapped**: US2 (FR-006, FR-010, FR-011, FR-012)

**API Endpoints Required**:
- POST /api/movements (movement_type=IN)

**Duration**: ~4 hours

### Backend Implementation

- [X] T033 [US2] Implement POST /api/movements for IN in `backend/src/api/movements.py`: validate MovementInCreate schema (quantity > 0, item_id exists), insert movement with timestamp=server NOW(), if unit_cost_override present update items.unit_cost in same transaction
- [X] T034 [US2] Add transaction wrapper in `backend/src/services/movement_service.py`: create_in_movement(item_id, quantity, movement_date, unit_cost_override, note) - BEGIN, INSERT movement, UPDATE item cost if override, COMMIT, handle rollback on error
- [X] T035 [US2] Add validation in `backend/src/api/movements.py`: Within ACID transaction, use `select(Item).where(Item.id == item_id).with_for_update()` to lock item row, check item_id exists (404 if not), validate quantity > 0 (400 if invalid), validate numeric format per FR-021 (max 3 decimal places, positive number), validate movement_date not >365 days past or future (400 if invalid), return Italian error messages. Row locking prevents concurrent negative stock edge cases.
- [X] T036 [US2] Add response schema in `backend/src/models/schemas.py`: MovementDetail includes item_name (denormalized for display), timestamp, all movement fields

### Frontend Implementation

- [X] T037 [P] [US2] Create MovementInForm component in `frontend/src/components/MovementInForm.tsx`: form fields (item_id autocomplete, quantity with react-number-format using Italian locale: decimalSeparator=",", thousandSeparator=".", decimalScale=3, allowNegative=false per FR-021; movement_date date picker default today, unit_cost_override optional with same number format, note textarea), submit button
- [X] T038 [US2] Add item autocomplete in `frontend/src/components/MovementInForm.tsx`: fetch items from /api/items, display name + current stock in dropdown, validate item selected before submit
- [X] T039 [US2] Add validation in `frontend/src/components/MovementInForm.tsx`: quantity > 0 (client-side check), show error "La quantità deve essere maggiore di zero", disable submit if invalid
- [X] T040 [US2] Integrate MovementInForm into Dashboard page in `frontend/src/pages/index.tsx`: "Carico (IN)" button opens modal/drawer with form, on success close form and refresh inventory table (SWR mutate)

**Checkpoint**: US2 complete - IN movements registrable, stock updates correctly, cost override works

---

## Phase 5: User Story 3 - Registrare Scarico Merce (OUT) (Priority: P3)

**Goal**: User can register OUT movements with confirmation dialog, system validates available stock

**Independent Test Criteria**:
1. Click "Scarico (OUT)" button → form opens
2. Select article "Pastiglie freno" with current stock 8
3. Enter quantity 2, date, note "Usato per riparazione Alfa Romeo 159"
4. Confirmation dialog shows "Stai per scaricare 2 unità di Pastiglie freno, giacenza disponibile 8"
5. Confirm → movement saved with quantity=-2, stock becomes 6
6. Attempt to discharge 10 units when stock is 3 → error "Impossibile scaricare 10 unità. Giacenza disponibile: 3"

**User Stories Mapped**: US3 (FR-007, FR-008, FR-009)

**API Endpoints Required**:
- POST /api/movements (movement_type=OUT)

**Duration**: ~4 hours

### Backend Implementation

- [X] T041 [US3] Implement POST /api/movements for OUT in `backend/src/api/movements.py`: validate MovementOutCreate schema (quantity > 0 user input, confirmed=true required), within ACID transaction use `select(Item).where(Item.id == item_id).with_for_update()` to lock item row, query current_stock with SUM(movements.quantity), check current_stock >= quantity (409 if insufficient), insert movement with quantity=-X (negated), COMMIT. Row locking prevents race conditions on concurrent OUT operations.
- [X] T042 [US3] Add stock validation in `backend/src/services/movement_service.py`: create_out_movement(item_id, quantity, movement_date, note, confirmed) - query SUM(movements.quantity) for item inside transaction (lock-free with MVCC), if current_stock < quantity raise InsufficientStock with available_stock in context
- [X] T043 [US3] Add error response in `backend/src/api/movements.py`: 409 Conflict for insufficient stock, ErrorResponse with detail="Impossibile scaricare X unità. Giacenza disponibile: Y", error_code="INSUFFICIENT_STOCK", context={requested_quantity, available_stock, unit}
- [X] T044 [US3] Add confirmation validation in `backend/src/api/movements.py`: if confirmed != true, return 400 "Conferma richiesta per scarico"

### Frontend Implementation

- [X] T045 [P] [US3] Create MovementOutForm component in `frontend/src/components/MovementOutForm.tsx`: form fields (item_id autocomplete with current stock display, quantity with react-number-format using Italian locale: decimalSeparator=",", thousandSeparator=".", decimalScale=3, allowNegative=false per FR-021; movement_date, note), submit triggers confirmation dialog
- [X] T046 [US3] Add confirmation dialog in `frontend/src/components/MovementOutForm.tsx`: before submit, fetch current stock for selected item, show modal "Stai per scaricare X unità di [Nome articolo], giacenza disponibile Y", require user click "Conferma" to proceed
- [X] T047 [US3] Add error handling in `frontend/src/components/MovementOutForm.tsx`: catch 409 InsufficientStock response, display error message "Impossibile scaricare X unità. Giacenza disponibile: Y" in red alert, block form submission
- [X] T048 [US3] Integrate MovementOutForm into Dashboard page in `frontend/src/pages/index.tsx`: "Scarico (OUT)" button opens modal with form, on success close and refresh inventory

**Checkpoint**: US3 complete - OUT movements registrable with confirmation, stock validation prevents negative inventory

---

## Phase 6: User Story 4 - Gestire Anagrafica Articoli (Priority: P4)

**Goal**: User can create, update, delete items with autocomplete for categories/units

**Independent Test Criteria**:
1. Click "Nuovo Articolo" → form opens
2. Enter name "Filtro abitacolo", category "Filtri" (autocomplete suggests existing categories), unit "pz", min_stock 5, unit_cost €8.50, notes "Formato universale"
3. Submit → item created with stock_quantity=0
4. Edit item: change unit_cost to €9.00 → saved successfully
5. Attempt to delete item with stock=5 → error "Impossibile eliminare: giacenza non zero"
6. Attempt to delete item with stock=0 but movements in last 6 months → error "Impossibile eliminare: l'articolo ha movimenti recenti (ultimi 12 mesi)"
7. Delete item with stock=0 and no movements in last 13 months → success after confirmation

**User Stories Mapped**: US4 (FR-013, FR-014, FR-015, FR-016, FR-017, FR-018)

**API Endpoints Required**:
- POST /api/items
- PUT /api/items/{id}
- DELETE /api/items/{id}
- GET /api/items/autocomplete/categories
- GET /api/items/autocomplete/units

**Duration**: ~6 hours

### Backend Implementation

- [X] T049 [US4] Implement POST /api/items in `backend/src/api/items.py`: validate ItemCreate schema (name NOT NULL, min_stock >= 0, unit_cost >= 0), check name uniqueness (409 if duplicate), insert item with created_at=NOW(), return ItemWithStock with stock_quantity=0
- [X] T050 [US4] Implement PUT /api/items/{id} in `backend/src/api/items.py`: validate ItemUpdate schema, fetch item by id (404 if not found), update all fields EXCEPT stock (read-only, modified via movements), set updated_at=NOW(), return updated ItemWithStock
- [X] T051 [US4] Implement DELETE /api/items/{id} in `backend/src/api/items.py`: fetch item (404 if not found), query current_stock (409 if stock > 0 with message "giacenza non zero"), query movements in last 12 months (409 if any exist with message "movimenti recenti"), delete item, return 204 No Content
- [X] T052 [P] [US4] Implement GET /api/items/autocomplete/categories in `backend/src/api/items.py`: SELECT DISTINCT category FROM items WHERE category IS NOT NULL ORDER BY category, optional query param 'q' for partial ILIKE filtering, return {categories: string[]}
- [X] T053 [P] [US4] Implement GET /api/items/autocomplete/units in `backend/src/api/items.py`: SELECT DISTINCT unit FROM items ORDER BY unit, return {units: string[]}
- [X] T054 [US4] Add name uniqueness check in `backend/src/services/item_service.py`: check_name_unique(name, exclude_id=None) - query items.name case-insensitive, raise DuplicateItemName if exists (use for both create and update)

### Frontend Implementation

- [X] T055 [P] [US4] Create ItemForm component in `frontend/src/components/ItemForm.tsx`: form fields (name required, category autocomplete, unit autocomplete default "pz", notes textarea, min_stock with react-number-format: decimalSeparator=",", thousandSeparator=".", decimalScale=3, allowNegative=false, default 0; unit_cost with same number format default 0 per FR-021), submit for create
- [X] T056 [US4] Add autocomplete for category in `frontend/src/components/ItemForm.tsx`: fetch categories from /api/items/autocomplete/categories, show dropdown suggestions on type, allow free text entry for new categories
- [X] T057 [US4] Add autocomplete for unit in `frontend/src/components/ItemForm.tsx`: fetch units from /api/items/autocomplete/units, show dropdown with common units (pz, kg, lt, m, kit), allow free text entry
- [X] T058 [US4] Create ItemEdit component in `frontend/src/components/ItemEdit.tsx`: reuse ItemForm with initial values from item, submit calls PUT /api/items/{id}
- [X] T059 [US4] Add delete confirmation in `frontend/src/components/ItemEdit.tsx`: "Elimina" button shows confirmation dialog "Sei sicuro di voler eliminare questo articolo?", on confirm call DELETE /api/items/{id}, handle 409 errors and display Italian error messages (giacenza non zero, movimenti recenti)

**Checkpoint**: US4 complete - items CRUD functional, autocomplete works, delete validations prevent data loss

---

## Phase 7: User Story 7 - Rettificare Inventario per Riconciliazione Fisica (Priority: P4)

**Goal**: User can register ADJUSTMENT movements with mandatory note, system calculates delta automatically

**Independent Test Criteria**:
1. Click "Rettifica" button → form opens
2. Select article "Filtro olio" with calculated stock 15
3. Enter target stock 13, note "Conteggio fisico mensile - 2 unità danneggiate"
4. Submit → movement created with movement_type=ADJUSTMENT, quantity=-2 (calculated), stock becomes 13
5. Attempt to enter target stock 15 (same as current) → error "La giacenza target coincide con quella attuale. Nessuna rettifica necessaria."
6. Attempt to submit without note → error "La nota è obbligatoria per le rettifiche (spiega il motivo della discrepanza)"
7. Enter target stock 20 (increase) → movement created with quantity=+5

**User Stories Mapped**: US7 (FR-036, FR-037, FR-038, FR-039, FR-040)

**API Endpoints Required**:
- POST /api/movements (movement_type=ADJUSTMENT)

**Duration**: ~4 hours

### Backend Implementation

- [X] T060 [US7] Implement POST /api/movements for ADJUSTMENT in `backend/src/api/movements.py`: validate MovementAdjustmentCreate schema (target_stock >= 0, note NOT NULL and length > 0), fetch current_stock inside transaction, calculate quantity=target_stock - current_stock, validate quantity != 0 (400 if zero with message "Nessuna rettifica necessaria"), insert movement with calculated quantity
- [X] T061 [US7] Add adjustment service in `backend/src/services/movement_service.py`: create_adjustment_movement(item_id, target_stock, movement_date, note) - query current_stock, compute delta, validate delta != 0, validate target_stock >= 0 (no negative stock), insert movement, COMMIT
- [X] T062 [US7] Add validation in `backend/src/api/movements.py`: check note is non-empty (400 if empty/whitespace with message "Nota obbligatoria per rettifiche"), check target_stock != current_stock (400 if equal), return MovementDetail with quantity showing calculated delta (+/-)
- [X] T063 [US7] Add adjustment display logic in `backend/src/models/schemas.py`: MovementDetail serialization shows quantity with sign (+/-) explicitly for ADJUSTMENT type

### Frontend Implementation

- [X] T064 [P] [US7] Create AdjustmentForm component in `frontend/src/components/AdjustmentForm.tsx`: form fields (item_id autocomplete showing current stock, target_stock number input, movement_date, note textarea REQUIRED), display calculated delta (target - current) in real-time as user types
- [X] T065 [US7] Add delta calculation preview in `frontend/src/components/AdjustmentForm.tsx`: show "Rettifica: +X unità" or "Rettifica: -X unità" based on target vs current stock, update in real-time
- [X] T066 [US7] Add validation in `frontend/src/components/AdjustmentForm.tsx`: note required (show error if empty), target_stock must differ from current (disable submit if equal with message "Nessuna rettifica necessaria"), target_stock >= 0 (no negative)
- [X] T067 [US7] Integrate AdjustmentForm into Dashboard page in `frontend/src/pages/index.tsx`: "Rettifica" button opens modal with form, on success close and refresh inventory

**Checkpoint**: US7 complete - ADJUSTMENT movements registrable, delta calculated automatically, note mandatory

---

## Phase 8: User Story 5 - Consultare Storico Movimenti (Priority: P5)

**Goal**: User can view movement history with filters (date range, item, type) and pagination

**Independent Test Criteria**:
1. Navigate to "Movimenti" page → see last 30 days movements in reverse chronological order (most recent first)
2. Filter by article "Olio motore 5W30" → see only movements for that item
3. Filter by type "OUT" → see only scarichi
4. Set date range 01/01/2025 to 31/03/2025 → see only movements in that period
5. Verify ADJUSTMENT movements show delta (+/-) clearly and include nota field
6. Verify IN movements with unit_cost_override show override value

**User Stories Mapped**: US5 (FR-022, FR-023, FR-024)

**API Endpoints Required**:
- GET /api/movements (with filters)
- GET /api/movements/{id}

**Duration**: ~4 hours

### Backend Implementation

- [X] T068 [US5] Implement GET /api/movements in `backend/src/api/movements.py`: query movements with filters (from_date default 30 days ago, to_date default today, item_id optional, movement_type optional IN/OUT/ADJUSTMENT/All), join with items for item_name, order by timestamp DESC, paginate (limit default 100, offset default 0), return {movements: MovementDetail[], total, limit, offset}
- [X] T069 [US5] Add date range filtering in `backend/src/services/movement_service.py`: list_movements(from_date, to_date, item_id, movement_type, limit, offset) - use indexes (idx_movements_movement_date, idx_movements_item_id, idx_movements_type), return paginated results
- [X] T070 [P] [US5] Implement GET /api/movements/{id} in `backend/src/api/movements.py`: fetch movement by id (404 if not found), join with items for item_name and unit, return MovementDetail
- [X] T071 [US5] Add movement formatting in `backend/src/models/schemas.py`: MovementDetail includes denormalized fields (item_name, unit) for display without additional queries

### Frontend Implementation

- [X] T072 [P] [US5] Create MovementTable component in `frontend/src/components/MovementTable.tsx`: display movements with columns (movement_date, item_name, movement_type with badge color, quantity with +/- sign for ADJUSTMENT, unit, unit_cost_override if present, note), sort by timestamp DESC
- [X] T073 [US5] Create MovementFilters component in `frontend/src/components/MovementFilters.tsx`: date range picker (from_date, to_date default last 30 days), item dropdown (fetch from /api/items), type dropdown (IN/OUT/ADJUSTMENT/Tutti), apply filters button
- [X] T074 [US5] Create Movimenti page in `frontend/src/pages/movimenti.tsx`: integrate MovementTable and MovementFilters, fetch movements from /api/movements with SWR, implement pagination (next/previous buttons), display total count

**Checkpoint**: US5 complete - movement history viewable, filters functional, pagination works

---

## Phase 9: User Story 6 - Esportare Dati in Excel (Priority: P6)

**Goal**: User can export inventory and last 12 months movements to .xlsx file client-side

**Independent Test Criteria**:
1. Click "Esporta Excel (ultimi 12 mesi)" button on dashboard
2. Browser downloads file named "magazzino_YYYYMMDD.xlsx"
3. Open file in Excel/LibreOffice → verify two sheets exist: "Inventario" and "Movimenti_ultimi_12_mesi"
4. "Inventario" sheet has columns: Nome, Categoria, Unità, Giacenza, Min. Scorta, Sotto Scorta (Sì/No), Costo Unitario, Valore (Giacenza×Costo), Note
5. Headers are bold, columns auto-width, numbers have 2 decimal places, EUR formatting for costs
6. "Movimenti_ultimi_12_mesi" sheet has columns: Data, Articolo, Tipo (IN/OUT/ADJUSTMENT), Quantità, Unità, Costo Unitario usato, Nota
7. Movements filtered to last 12 months from today, sorted by date

**User Stories Mapped**: US6 (FR-025, FR-026, FR-027, FR-028, FR-029)

**API Endpoints Required**:
- GET /api/export/preview (metadata only, client generates .xlsx)

**Duration**: ~4 hours

### Backend Implementation

- [X] T075 [US6] Implement GET /api/export/preview in `backend/src/api/export.py`: return {export_date, period_start (12 months ago), period_end (today), inventory: ItemWithStock[], movements: MovementDetail[] filtered to last 12 months}
- [X] T076 [US6] Add export data service in `backend/src/services/export_service.py`: get_export_data() - query all items with current_stock, query movements WHERE movement_date >= CURRENT_DATE - INTERVAL '12 months' ORDER BY movement_date, return JSON structure for client-side Excel generation

### Frontend Implementation

- [X] T077 [P] [US6] Install SheetJS in `frontend/`: npm install xlsx (SheetJS provides better performance for 5K-10K rows per SC-004, lower memory usage than ExcelJS)
- [X] T078 [US6] Create Excel generation utility in `frontend/src/services/exportExcel.ts` using SheetJS: generateExcel(exportData) - Pre-format data as Italian locale strings (numbers with comma decimal separator "1.234,56", dates "DD/MM/YYYY", currency "€X.XXX,XX", "Sì"/"No" for under_stock), use XLSX.utils.json_to_sheet() to create "Inventario" and "Movimenti_ultimi_12_mesi" sheets, XLSX.utils.book_new() for workbook, set column widths via !cols property, return workbook
- [X] T079 [US6] Add sheet styling in `frontend/src/services/exportExcel.ts` with SheetJS: Set column widths via worksheet['!cols'] array with {wch: width} objects, apply basic formatting (note: SheetJS community edition has limited cell styling vs ExcelJS, but sufficient for basic exports). Pre-formatted Italian strings in T078 handle number/date/currency display.
- [X] T080 [US6] Integrate export button into Dashboard page in `frontend/src/pages/index.tsx`: "Esporta Excel (ultimi 12 mesi)" button calls /api/export/preview, generates .xlsx with SheetJS using XLSX.writeFile(workbook, filename), triggers browser download with filename "magazzino_YYYYMMDD.xlsx". SheetJS handles file download automatically.

**Checkpoint**: US6 complete - Excel export functional, file downloadable, formatting correct, all user stories delivered

---

## Phase 10: Polish & Deployment

**Purpose**: Production readiness, deployment, documentation, performance optimization

**Duration**: ~8 hours

### Code Quality & Performance

- [X] T081 [P] Add Italian error messages for all API endpoints in `backend/src/api/errors.py`: centralize error message constants
- [X] T082 [P] Add Italian i18n for all frontend strings in `frontend/src/i18n/it.json`: complete translation for all UI labels, buttons, messages
- [X] T083 [P] Add input validation feedback in all frontend forms: real-time validation with Italian error messages, disable submit until valid
- [X] T083.1 [P] Create validation utilities in `backend/src/services/validation.py` per FR-021: validate_decimal(value, max_digits=10, decimal_places=3) checks numeric format with max 3 decimals, validate_positive(value) ensures value > 0, validate_date_range(date, max_past_days=365, allow_future=False) validates movement dates, validate_quantity(quantity, movement_type) combines decimal + positive checks, return ValidationError with Italian messages
- [X] T083.2 [P] Create Italian locale validation checklist in `frontend/tests/locale-validation.md`: verify all UI strings use it.json (no hardcoded English), date format DD/MM/YYYY throughout, number format 1.234,56 (comma decimal separator, dot thousands), currency €X.XXX,XX format, all error messages in Italian, verify with native Italian speaker before production deploy
- [ ] T084 [P] Add loading states in all frontend components: skeleton loaders for tables, spinner for buttons during API calls, optimistic updates with SWR
- [ ] T085 Add performance optimization in `backend/src/services/stock_service.py`: cache current_stock view query results for 5 seconds (invalidate on mutations)
- [X] T086 [DEPRECATED - moved to T032.1 in MVP Phase 3] Keyboard navigation now implemented in Phase 3 for accessibility priority
- [X] T087 [P] Create backend health check endpoint in `backend/src/main.py`: GET /health returns {status: "ok", timestamp, db_connected: boolean}

### Database & Migrations

- [X] T088 Create seed data script in `backend/scripts/seed_data.py`: insert 10 sample items (Olio motore, Filtro olio, Pastiglie freno, etc.) with categories, units, costs, min_stocks, plus 20 sample movements (IN/OUT/ADJUSTMENT mix) for testing
- [ ] T089 Test migration rollback in `backend/alembic/versions/001_initial_schema.py`: ensure downgrade() correctly drops tables and extensions
- [ ] T090 Add database backup instructions in quickstart.md: pg_dump command for local backup, Neon dashboard backup for production

### Deployment Configuration

- [ ] T091 Create Neon PostgreSQL database: sign up at neon.tech, create project "inventario-magazzino", enable extensions (uuid-ossp, pg_trgm), get connection string
- [ ] T092 Deploy backend to Render: create web service from GitHub repo, configure environment variables (DATABASE_URL from Neon, CORS_ORIGINS for Vercel frontend), set build command "pip install -r requirements.txt", start command "uvicorn app.main:app --host 0.0.0.0 --port 8000"
- [ ] T093 Run migrations on production database: export DATABASE_URL for Neon, run "alembic upgrade head" from local machine, verify tables and views created
- [ ] T094 Deploy frontend to Vercel: import GitHub repo, set root directory "frontend", configure environment variables (NEXT_PUBLIC_API_URL pointing to Render backend), deploy with auto-build
- [ ] T095 Update CORS in production backend: add Vercel frontend URL to CORS_ORIGINS in Render environment variables, redeploy backend
- [ ] T096 Test production deployment: open Vercel frontend URL, create item, register movements (IN/OUT/ADJUSTMENT), export Excel, verify data persists

### Documentation & Testing

- [ ] T097 Validate quickstart.md accuracy: follow setup instructions step-by-step on clean machine, update any outdated commands or configurations
- [ ] T098 Create production monitoring checklist: Render logs (backend errors), Neon dashboard (query stats, storage usage), Vercel analytics (page load times), uptime monitoring with UptimeRobot (optional ping to /health endpoint)

**Checkpoint**: Production deployed - frontend on Vercel, backend on Render, database on Neon, all user stories functional in production

---

## Parallel Execution Examples

### Phase 2 (Foundational) Parallelization
```bash
# These can run simultaneously (different files):
- T013: backend/src/models/item.py
- T014: backend/src/models/movement.py
- T018: backend/src/api/errors.py
```

### Phase 3 (US1) Parallelization
```bash
# Backend endpoints can run in parallel:
- T019: backend/src/api/items.py (GET /api/items)
- T021: backend/src/api/dashboard.py (GET /api/dashboard/stats)

# Frontend components can run in parallel:
- T024: frontend/src/components/ItemTable.tsx
- T025: frontend/src/components/SearchBar.tsx
- T026: frontend/src/components/CategoryFilter.tsx
- T027: frontend/src/components/UnderStockToggle.tsx
- T028: frontend/src/components/DashboardStats.tsx
```

### Multi-Story Parallelization (After Phase 2)
```bash
# Different user stories can be developed simultaneously:
Developer A: Phase 3 (US1 - Dashboard)
Developer B: Phase 4 (US2 - IN movements)
Developer C: Phase 5 (US3 - OUT movements)
Developer D: Phase 6 (US4 - Items CRUD)
```

---

## Validation Checklist

After completing all phases, verify:

### Functional Requirements
- [ ] FR-001: Dashboard shows real-time stock (SUM of movements)
- [ ] FR-002: Name search works (partial, case-insensitive)
- [ ] FR-003: Category filter works
- [ ] FR-004: "Solo sotto scorta" toggle works
- [ ] FR-005: Under-stock items visually highlighted
- [ ] FR-006: IN movements registrable with optional cost override and note
- [ ] FR-007: OUT movements registrable with note
- [ ] FR-008: OUT movements blocked if stock insufficient
- [ ] FR-009: OUT movements require confirmation dialog
- [ ] FR-010: Unit cost updated when IN has cost override
- [ ] FR-011: Timestamps are server-side
- [ ] FR-012: All movements atomic (transactions)
- [ ] FR-013: Items creatable with all fields
- [ ] FR-014: Items updatable (except stock)
- [ ] FR-015: Items deletable only if stock=0 and no movements in 12 months
- [ ] FR-016: Delete blocked if stock > 0
- [ ] FR-017: Delete blocked if recent movements
- [ ] FR-018: Autocomplete works for categories and units
- [ ] FR-019: Quantity validation (> 0)
- [ ] FR-020: Name validation (not empty)
- [ ] FR-021: Numeric validation (min_stock, unit_cost, quantities)
- [ ] FR-022: Movement history with filters (date, item, type)
- [ ] FR-023: Movements show all fields (date, item, type, quantity, cost, note)
- [ ] FR-024: Movements ordered DESC by date (most recent first)
- [ ] FR-025-029: Excel export generates .xlsx with 2 sheets, Italian formatting, last 12 months filter
- [ ] FR-036: ADJUSTMENT movements registrable
- [ ] FR-037: ADJUSTMENT quantity calculated as delta
- [ ] FR-038: ADJUSTMENT blocked if target = current
- [ ] FR-039: ADJUSTMENT note mandatory
- [ ] FR-040: ADJUSTMENT shows delta (+/-) in history
- [ ] FR-041: Dashboard shows total warehouse value
- [ ] FR-042: Dashboard shows under-stock count

### Success Criteria
- [ ] SC-001: Movement registration < 30 seconds
- [ ] SC-002: Stock updates in < 1 second
- [ ] SC-003: 100% prevention of negative stock (except ADJUSTMENT with note)
- [ ] SC-004: Excel export < 10 seconds for 5000+ movements
- [ ] SC-005: Under-stock items identifiable in < 5 seconds
- [ ] SC-006: 90% first-time success without help
- [ ] SC-007: 100% data consistency (no negative stock, no zero quantity movements, atomic transactions)
- [ ] SC-008: Excel file opens without errors, correct formatting
- [ ] SC-009: System handles 1000 items + 10000 movements, pages load < 2 seconds
- [ ] SC-010: Keyboard navigation works (Tab, Enter, Escape)
- [ ] SC-011: Total warehouse value accurate and real-time
- [ ] SC-012: Under-stock banner visible when applicable

---

## Notes

- **[P] tasks**: Different files, no dependencies, can run in parallel
- **[Story] label**: Maps task to user story for traceability (US1-US7)
- **File paths**: All paths relative to repository root or absolute
- **Tests**: Not included (tests not requested in spec.md)
- **Dependencies**: Phase 2 BLOCKS all user stories, but user stories (Phase 3-9) can run in parallel after Phase 2 completes
- **MVP strategy**: Complete Phase 1+2+3 (US1) for minimum viable product, then add US2-US7 incrementally
- **Deployment**: Free tier (Vercel + Render + Neon), cold starts ~2-5 seconds acceptable for single-user
- **Italian locale**: All UI strings, error messages, date/number formatting in Italian
- **Event sourcing**: Movements are immutable, stock is computed on-the-fly from SUM(movements.quantity)

---

**Total Implementation Time Estimate**: ~50 hours (Setup: 2h, Foundational: 6h, US1: 8h, US2: 4h, US3: 4h, US4: 6h, US7: 4h, US5: 4h, US6: 4h, Polish: 8h)

**Recommended Approach**: Complete MVP (Phase 1+2+3 = US1) first (~16 hours), validate with user, then add US2-US7 incrementally based on priority.
