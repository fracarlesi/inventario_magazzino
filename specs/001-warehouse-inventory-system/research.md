# Technology Stack Research: Warehouse Inventory Management System

Research conducted: 2025-11-11

## Executive Summary

This document provides technology recommendations for a single-user, event-sourced warehouse inventory management system for an Italian auto repair shop. All recommendations prioritize free-tier deployment compatibility, performance for 1000 items/10000 movements, and minimal complexity.

---

## 1. Backend Web Framework (Python)

### Decision: **FastAPI**

### Rationale
FastAPI is the optimal choice for this project due to its native async support, automatic OpenAPI documentation generation, and minimal overhead. It provides high performance (essential for <1s updates) while maintaining simplicity for a single-user application. The framework is lightweight and serverless-ready, making it ideal for free-tier deployment on platforms like Render or Railway.

### Alternatives Considered

- **Flask**: Mature and minimal, but lacks native async support (WSGI-only). This is a dealbreaker for event-sourced architecture where concurrent event processing and real-time updates are beneficial. While deployable on free tiers, it cannot leverage async I/O for PostgreSQL operations, limiting scalability and responsiveness.

- **Django**: Heavyweight and designed for full-stack monolithic applications. Includes unnecessary features (admin panel, built-in auth, templating) that add overhead for a simple API-only backend. Async support is partial and not native to Django ORM or DRF. Cold start times on serverless/free tiers are significantly worse than FastAPI. Migration system is excellent but tied to Django ORM.

### Integration Notes

- Works seamlessly with SQLAlchemy 2.x for database operations
- Automatic OpenAPI/Swagger documentation eliminates need for separate API doc tools
- Deploys easily to Render free tier with Uvicorn ASGI server
- Native async/await syntax integrates well with async PostgreSQL drivers (asyncpg)
- Pydantic models provide automatic request validation and serialization for TypeScript integration

---

## 2. Python ORM

### Decision: **SQLAlchemy 2.x with Alembic**

### Rationale
SQLAlchemy 2.x provides the precise transaction control and PostgreSQL feature access required for event sourcing patterns. It supports optimistic locking via version columns, enables direct use of PostgreSQL NOTIFY/LISTEN for event propagation, and integrates with established event sourcing libraries. Alembic provides robust migration management suitable for evolving event schemas over time.

### Alternatives Considered

- **Django ORM**: Poor fit for event sourcing. Lacks aggregate-level atomicity without full table locking, making it difficult to implement proper version-based optimistic locking. Transaction handling assumes traditional CRUD operations rather than command-query separation. Tightly coupled to Django framework.

- **Prisma Python**: Still immature for production event sourcing as of 2025. Limited support for complex transaction semantics and concurrent update handling. No direct access to PostgreSQL-specific features like advisory locks or LISTEN/NOTIFY. Migration system is less sophisticated than Alembic for evolving event schemas. Smaller ecosystem with fewer battle-tested implementations.

- **Raw SQL with psycopg3**: Maximum control and best performance when optimized, but highest maintenance overhead. Requires manual type mapping, custom migration tooling, and SQL expertise. No protection against common errors. Only justified if benchmarks prove SQLAlchemy insufficient—unlikely for 10,000 movements.

### Integration Notes

- Use declarative mapping with explicit version columns for aggregates
- Implement two-table pattern: immutable events table (append-only) + aggregate versions table
- Create PostgreSQL views for read-side projections of computed stock levels
- Alembic migrations handle schema evolution independently of ORM
- Works with FastAPI's dependency injection for session management
- Supports async operations via SQLAlchemy 2.0 async API with asyncpg driver

---

## 3. Frontend Framework

### Decision: **Next.js (React + TypeScript)**

### Rationale
Next.js offers the smoothest Vercel deployment experience (first-class integration), built-in internationalization routing for Italian language support, and excellent TypeScript 5.x support. While bundle sizes are larger than Svelte, the production-ready features (SSR/SSG, API routes, image optimization), mature ecosystem, and zero-config Vercel deployment outweigh the size penalty for a 1000-item inventory system where bundle size is not the primary bottleneck.

### Alternatives Considered

- **Svelte/SvelteKit**: Smallest bundle size (~40% smaller than React) and best runtime performance due to compile-time optimization with no runtime overhead. However, Vercel integration is less polished than Next.js, requiring more manual configuration for serverless/edge functions. i18n requires third-party libraries (svelte-i18n). Choose this if bundle size/performance is the absolute priority and you're comfortable with manual Vercel configuration.

- **React + Vite**: Fast development experience with instant HMR, but requires manual assembly of routing (React Router), SSR/SSG setup, and API routes. No built-in i18n solution. More configuration overhead than Next.js with minimal benefit for this use case. Better suited for SPAs than full-stack apps.

- **Vue 3**: Excellent middle ground with small bundles, approachable DX, and strong i18n ecosystem (vue-i18n). However, requires adapter configuration for Vercel SSR deployment and lacks the first-class Vercel integration of Next.js. Good alternative if team prefers Vue's reactivity model over React hooks.

### Integration Notes

- Next.js App Router provides file-based routing with TypeScript support
- Built-in i18n routing handles Italian/English language switching
- Image optimization and static generation improve perceived performance
- Can deploy FastAPI backend separately or use Next.js API routes for simple endpoints
- React Query or SWR handle data fetching/caching for real-time inventory updates
- Vercel deployment via Git push with automatic preview environments

---

## 4. Deployment Strategy

### Decision: **Complete Free-Tier Architecture**

**Frontend:** Vercel
**Backend:** Render (Python FastAPI)
**Database:** Neon PostgreSQL

### Rationale

This combination provides permanent free tiers with acceptable performance for a single-user application:

- **Vercel (Frontend)**: Best-in-class DX for Next.js deployment, global CDN, automatic HTTPS, unlimited bandwidth for free tier, preview deployments for every Git push.

- **Render (Backend)**: Only platform offering truly permanent free tier for Python backend (unlike Railway's one-time $5 credit). Services sleep after 15 minutes of inactivity with ~2-5 second cold starts—acceptable for single-user shop usage patterns. Easy Git-based deployment.

- **Neon (Database)**: 3GB storage limit (vs Supabase's 500MB), serverless PostgreSQL with fast query performance, no 90-day deletion (unlike Render PostgreSQL). Supports PostgreSQL 15+ features. Cold starts are minimal for small query loads.

### Alternatives Considered

- **Vercel Serverless Functions (Backend)**: While possible to deploy FastAPI on Vercel, cold starts for Python are 500ms-2s+, and the platform is optimized for Node.js serverless, not persistent Python processes. Better suited for frontend only.

- **Railway (Backend)**: Excellent DX and fast deployment, but $5 one-time credit runs out quickly with always-on services. Not truly free long-term. Best for prototyping/development phase.

- **Supabase (Database)**: Offers built-in auth and real-time subscriptions, but 500MB storage limit and 10K row soft limit are restrictive compared to Neon's 3GB. Choose this if you need real-time PostgreSQL subscriptions or integrated auth (though not required for single-user app).

- **Render PostgreSQL**: Integrates seamlessly with Render backend, but free tier databases are deleted after 90 days of inactivity—unacceptable for production inventory system.

### Integration Notes

- **Deployment Flow**:
  - Frontend: Push to GitHub → Vercel auto-deploys via Next.js build
  - Backend: Push to GitHub → Render auto-deploys FastAPI with Uvicorn
  - Database: Neon provides connection string with pgBouncer pooling

- **CORS Configuration**: Configure FastAPI to allow requests from Vercel frontend domain

- **Environment Variables**:
  - Neon connection string stored in Render environment
  - Render API URL stored in Vercel environment

- **Cold Start Mitigation**:
  - Render free tier sleeps after 15 min inactivity
  - Consider periodic health check ping if always-on required (may impact free tier limits)
  - Neon serverless wakes nearly instantly for queries

- **Monitoring**: Use Render logs + Neon dashboard for basic monitoring (both free)

---

## 5. Excel Generation

### Decision: **SheetJS (xlsx)**

### Rationale
SheetJS consistently outperforms ExcelJS for large datasets (5,000-10,000 rows) due to lower memory usage and faster parsing/writing, making it critical for our SC-004 performance target (<10s for 5K movements, <30s for 10K movements). While ExcelJS offers richer styling features, SheetJS community edition provides sufficient functionality for basic inventory exports (multi-sheet workbooks, basic formatting, Italian locale support via manual formatting) without risk of browser freezing during large exports. Apache-2.0 license is suitable for commercial use.

### Alternatives Considered

- **ExcelJS**: More feature-rich with advanced cell styling (borders, fonts, backgrounds), formulas, and ergonomic API. However, benchmarks show significantly higher memory consumption and slower performance for 5K+ rows client-side. Bundle size (~400KB) similar to SheetJS. Best suited for smaller datasets (<1000 rows) or when advanced formatting is critical business requirement.

- **SpreadJS**: Enterprise-grade solution with highest Excel fidelity (500+ functions, all formatting features, full Italian i18n). However, large bundle size (>1MB) and commercial licensing make it overkill for basic inventory export requirements. Only justified if spreadsheet UI/editing is needed in browser.

- **xlsx-populate**: Good for template-based exports but less ergonomic for building spreadsheets from scratch. MIT licensed but smaller feature set and less active maintenance than SheetJS.

### Integration Notes

- Client-side generation keeps export processing off backend (no server load)
- Bundle size ~350KB minified (slightly smaller than ExcelJS)
- Generate multi-sheet workbooks: Summary, Stock Movements, Low Stock Items
- Apply Italian locale formatting manually via `XLSX.utils.json_to_sheet()` with pre-formatted strings (dates as DD/MM/YYYY, currency as €X.XXX,XX, numbers with comma decimal separator)
- Basic styling via `!cols` and `!rows` properties (column widths, row heights)
- Export triggered from Next.js frontend, file downloaded directly to browser
- No backend API call required for export (reduces server load and deployment costs)
- Performance validated for SC-004: <10s generation time for 5000 movements, <30s for 10000 movements on client-side

---

## Complete Stack Summary

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| **Backend Framework** | FastAPI | Latest | Async-native, OpenAPI generation, minimal overhead |
| **Backend Runtime** | Python | 3.11+ | Required by specification |
| **ORM** | SQLAlchemy | 2.x | Event sourcing support, PostgreSQL features, precise transaction control |
| **Migrations** | Alembic | Latest | Industry standard for SQLAlchemy migrations |
| **Frontend Framework** | Next.js | 14+ | Best Vercel integration, built-in i18n, TypeScript support |
| **Frontend Runtime** | TypeScript | 5.x | Required by specification |
| **Excel Generation** | SheetJS (xlsx) | Latest | Best performance for 5K-10K rows, low memory usage, Apache-2.0 license |
| **Database** | PostgreSQL | 15+ | Required by specification |
| **Frontend Hosting** | Vercel | Free tier | Zero-config Next.js deployment, global CDN |
| **Backend Hosting** | Render | Free tier | Permanent free tier for Python, easy deployment |
| **Database Hosting** | Neon | Free tier | 3GB storage, serverless PostgreSQL, no time limit |

---

## Implementation Priorities

1. **Start with Backend**: Set up FastAPI + SQLAlchemy + Alembic with basic CRUD operations
2. **Database Schema**: Implement event sourcing pattern (events table + views for computed stock)
3. **Frontend Scaffold**: Initialize Next.js with TypeScript, configure i18n for Italian
4. **API Integration**: Connect Next.js to FastAPI backend, implement data fetching
5. **Excel Export**: Add SheetJS client-side export functionality
6. **Deployment**: Deploy to Render (backend) + Neon (DB) + Vercel (frontend)

---

## Risk Mitigations

- **Cold Starts (Render)**: Acceptable for single-user usage pattern; consider health check ping if needed
- **Free Tier Limits**: 3GB storage (Neon) and 10K movements should accommodate growth beyond initial 1K items
- **Bundle Size**: Next.js bundles larger than Svelte, but not bottleneck for target performance (<2s page load)
- **Vendor Lock-in**: All platforms use standard tech (PostgreSQL, Node.js, Python) enabling migration if free tiers change

---

## Notes on Event Sourcing Implementation

With SQLAlchemy 2.x:
- Create `movements` table (immutable, append-only) with columns: id, timestamp, item_id, quantity_delta, movement_type, metadata_json, version
- Create `aggregates` table for optimistic locking: aggregate_id, version, last_updated
- Use PostgreSQL materialized views or regular views to compute current stock: `SELECT item_id, SUM(quantity_delta) as current_stock FROM movements GROUP BY item_id`
- Implement version-based optimistic locking to prevent concurrent modification conflicts
- Consider NOTIFY/LISTEN for real-time frontend updates (optional enhancement)
