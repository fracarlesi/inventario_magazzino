# Implementation Plan: Sistema di Gestione Magazzino Officina

**Branch**: `001-warehouse-inventory-system` | **Date**: 2025-11-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-warehouse-inventory-system/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Sistema web-based per gestione inventario magazzino di una singola officina auto. Permette registrazione movimenti IN/OUT/ADJUSTMENT, visualizzazione real-time giacenze con alert sotto scorta, gestione anagrafica articoli, storico completo movimenti, e export Excel ultimi 12 mesi. Architettura event-sourced con giacenze calcolate, interfaccia italiana per utenti non-tecnici, focus su data integrity e semplicità operativa.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI (backend), SQLAlchemy 2.x + Alembic (ORM/migrations), Next.js 14+ (frontend), ExcelJS (client-side export)
**Storage**: PostgreSQL 15+ via Neon (event-sourced movements, computed giacenze with views)
**Testing**: pytest (backend), Vitest (frontend), Playwright (e2e)
**Target Platform**: Web browser (Chrome/Firefox/Safari last 2 years), Render (backend), Vercel (frontend), Neon (database)
**Project Type**: Web application (frontend + backend REST API)
**Performance Goals**: <2s page load, <1s giacenza update, <10s Excel export (5000+ movements)
**Constraints**: Free tier compatible (Render + Vercel + Neon), single-user (no auth initially), Italian locale, ~2-5s cold starts acceptable
**Scale/Scope**: ~1000 articoli, ~10000 movimenti, 7 user stories, ~45 functional requirements

**Stack Rationale**: See [research.md](./research.md) for detailed technology decisions.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Simplicity First ✅ PASS
- **Evaluation**: Sistema focalizzato su core operations (IN/OUT/ADJUSTMENT, inventory view, export). Nessuna feature enterprise (multi-tenancy, complex permissions, workflow).
- **Justification**: Single-user, single-shop. Architettura event-sourced è semplice e appropriata per audit trail. Zero over-engineering.

### II. Data Integrity (NON-NEGOTIABLE) ✅ PASS
- **Evaluation**:
  - FR-012: Atomic transactions guaranteed
  - FR-011: Server-side timestamps
  - FR-008: Prevents negative stock
  - FR-036-040: ADJUSTMENT movements with mandatory notes for audit
  - Event sourcing: immutable movements, computed giacenze
- **Justification**: 100% compliant. Complete audit trail, no data loss risk, transactional consistency enforced.

### III. User-Centric Interface ✅ PASS
- **Evaluation**:
  - FR-030-034: Clear buttons, Italian messages, keyboard navigation
  - FR-031: Helpful placeholders
  - FR-033: Confirmations for destructive actions
  - FR-041-042: Dashboard shows total value + stock alerts
  - SC-006: 90% first-time success without training
  - SC-001: <30s per operation
- **Justification**: Interface designed for non-technical officina staff. All UX requirements met.

### IV. Single-Source Architecture ✅ PASS
- **Evaluation**:
  - No authentication system (single-user assumption)
  - No multi-tenancy
  - Database design optimized for single shop
  - Deployment targets free tier (realistic for single user)
- **Justification**: Architecture reflects reality. No scale-for-future waste.

**GATE RESULT: PASS** - All constitutional principles respected. No violations to justify.

---

### Post-Design Re-Evaluation (After Phase 1)

**Re-evaluated**: 2025-11-11 after data-model.md, contracts/openapi.yaml, quickstart.md generation

#### I. Simplicity First ✅ PASS
- **Data Model**: Two tables (items + movements) + one computed view. No complex aggregates, no denormalization.
- **API Design**: 12 REST endpoints with standard CRUD patterns. No GraphQL, no complex subscriptions.
- **Technology Choices**: Standard FastAPI + SQLAlchemy + Next.js stack. No microservices, no message queues.
- **Verdict**: Design remains simple and focused. Event sourcing pattern is appropriate (not over-engineered).

#### II. Data Integrity (NON-NEGOTIABLE) ✅ PASS
- **Database Constraints**: 10 CHECK constraints enforce business rules at DB level
- **Transactions**: All write operations documented with atomic transaction boundaries
- **Audit Trail**: Immutable movements table with server timestamps (created_at)
- **Validation**: Both database-level (constraints) and application-level (Pydantic) validation
- **Verdict**: Excellent integrity safeguards. Event sourcing provides complete audit trail.

#### III. User-Centric Interface ✅ PASS
- **API Errors**: Italian error messages in all 4xx/5xx responses
- **Autocomplete**: Dedicated endpoints for category/unit suggestions (FR-018)
- **Confirmations**: `confirmed` field required for OUT movements (FR-009)
- **Performance**: Indexes on all filter columns (<2s query targets)
- **Verdict**: Backend properly supports UX requirements. Frontend implementation will leverage these endpoints.

#### IV. Single-Source Architecture ✅ PASS
- **No Auth**: API has no authentication endpoints (single-user assumption maintained)
- **Deployment**: Single backend + single frontend + single database (no multi-region, no sharding)
- **Scaling**: Schema designed for ~10K movements (appropriate, not over-provisioned)
- **Verdict**: Architecture correctly reflects single-shop reality. No premature optimization.

**POST-DESIGN GATE RESULT: PASS** - Design phase introduces no constitutional violations. Ready for tasks generation.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/          # Item, Movement entities
│   ├── services/        # Business logic (giacenza calculation, validations)
│   ├── api/             # REST endpoints (items, movements, export)
│   └── db/              # Database migrations, connection
├── tests/
│   ├── unit/            # Service logic, calculations
│   ├── integration/     # API endpoints with test DB
│   └── fixtures/        # Test data
└── pyproject.toml       # Python dependencies

frontend/
├── src/
│   ├── components/      # Reusable UI (ItemTable, MovementForm, StockAlert)
│   ├── pages/           # Dashboard, Movimenti, Articoli, Export
│   ├── services/        # API client, Excel generation (SheetJS)
│   ├── types/           # TypeScript interfaces
│   └── i18n/            # Italian localization
├── tests/
│   ├── unit/            # Component tests
│   └── e2e/             # End-to-end with Playwright
└── package.json         # Node dependencies

shared/
└── contracts/           # OpenAPI spec (generated Phase 1)

.specify/                # Project management
└── [as provided by template]
```

**Structure Decision**: Web application (Option 2). Backend serves REST API with PostgreSQL persistence, frontend is SPA consuming API and generating client-side Excel exports. Shared `/contracts/` directory for API contract (OpenAPI schema) used by both backend validation and frontend client generation.

## Terminology Standards

To maintain consistency across Italian UI/documentation and English codebase:

### Italian (UI, User-Facing Documentation, Error Messages)
- **giacenza** - stock quantity/inventory level
- **carico** - IN movement (receiving goods)
- **scarico** - OUT movement (using/consuming goods)
- **rettifica** - ADJUSTMENT (inventory correction)
- **articolo** - item/product
- **scorta minima** - minimum stock threshold
- **sottoscorta** - under minimum stock (alert state)

### English (Code, Database Schema, API, Technical Docs)
- **stock_quantity** - computed current stock from movements
- **movement_type** - IN, OUT, ADJUSTMENT enum
- **item** - product/article entity
- **min_stock** - minimum stock threshold field
- **is_under_min_stock** - boolean flag for alerts

### Database Column Naming
- Use English snake_case: `stock_quantity`, `movement_type`, `min_stock`, `unit_cost`
- PostgreSQL compatibility: avoid Italian accents/special characters

### API Naming
- REST endpoints use English plurals: `/api/items`, `/api/movements`
- Query parameters use English: `?search=`, `?category=`, `?under_stock_only=`
- Response schemas use English field names matching database

### Frontend Code
- Component names use English: `ItemTable`, `MovementInForm`, `DashboardStats`
- Props and state variables use English: `stockQuantity`, `movementType`, `isUnderMinStock`
- Display strings use Italian from `i18n/it.json`: load translations dynamically

**Rationale**: Separation allows developers to work in standard English codebase while ensuring end users see Italian throughout the interface. No mixing of languages within the same context (no "giacenza_quantity" or similar hybrid terms).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations detected.** Constitution Check passed all gates.
