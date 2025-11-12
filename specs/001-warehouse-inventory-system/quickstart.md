# Quickstart Guide: Warehouse Inventory System

**Version:** 1.0
**Last Updated:** 2025-11-11
**Stack:** FastAPI + SQLAlchemy + Next.js + PostgreSQL

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Environment Variables](#environment-variables)
4. [Database Migrations](#database-migrations)
5. [Testing](#testing)
6. [API Documentation](#api-documentation)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)
9. [Useful Commands](#useful-commands)

---

## Prerequisites

Before starting, ensure you have the following software installed on your local machine:

### Required Software

| Software | Version | Download Link | Purpose |
|----------|---------|--------------|---------|
| **Python** | 3.11+ | [python.org](https://www.python.org/downloads/) | Backend runtime |
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org/) | Frontend runtime |
| **PostgreSQL** | 15+ | [postgresql.org](https://www.postgresql.org/download/) | Database |
| **Git** | Latest | [git-scm.com](https://git-scm.com/) | Version control |

### Optional but Recommended

- **Docker Desktop** (for containerized PostgreSQL)
- **pgAdmin** or **DBeaver** (for database GUI)
- **Postman** or **Insomnia** (for API testing)

### System Requirements

- **RAM:** 4GB minimum (8GB recommended)
- **Storage:** 1GB free space
- **OS:** macOS, Linux, or Windows 10/11 with WSL2

---

## Local Development Setup

### 1. Database Setup

#### Option A: Local PostgreSQL Installation

**macOS (Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql-15 postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download and install from [postgresql.org](https://www.postgresql.org/download/windows/)

**Create the database:**
```bash
# Connect to PostgreSQL
psql postgres

# Inside psql, create database and user
CREATE DATABASE inventario_magazzino;
CREATE USER warehouse_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE inventario_magazzino TO warehouse_user;
ALTER DATABASE inventario_magazzino OWNER TO warehouse_user;
\q
```

#### Option B: Docker PostgreSQL (Recommended for Development)

Create a `docker-compose.yml` in the project root:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: inventario_postgres
    environment:
      POSTGRES_DB: inventario_magazzino
      POSTGRES_USER: warehouse_user
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U warehouse_user -d inventario_magazzino"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

Start the container:
```bash
docker-compose up -d
```

**Enable required PostgreSQL extensions:**
```bash
# Connect to the database
psql -h localhost -U warehouse_user -d inventario_magazzino

# Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
\q
```

---

### 2. Backend Setup

#### Clone the Repository

```bash
# Clone the repo
git clone https://github.com/your-org/inventario_magazzino.git
cd inventario_magazzino

# Switch to the feature branch (if needed)
git checkout 001-warehouse-inventory-system
```

#### Create Python Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate
```

#### Install Backend Dependencies

```bash
# Navigate to backend directory
cd backend

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**Expected `requirements.txt` packages:**
```txt
fastapi==0.104.0
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.0
```

#### Initialize Database Migrations

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Generate initial migration
alembic revision --autogenerate -m "Initial schema with items and movements tables"

# Apply migrations
alembic upgrade head
```

#### Run the Backend Server

```bash
# Start FastAPI development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify the backend:**
```bash
curl http://localhost:8000/api/items
# Expected: {"items": [], "total": 0, "filtered": 0}
```

---

### 3. Frontend Setup

Open a new terminal (keep the backend running).

#### Install Frontend Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

**Expected `package.json` dependencies:**
```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "xlsx": "^0.18.5",
    "swr": "^2.2.4",
    "react-number-format": "^5.3.0",
    "@tanstack/react-table": "^8.11.0",
    "next-i18next": "^15.0.0",
    "axios": "^1.6.0",
    "tailwindcss": "^3.3.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "vitest": "^1.0.0",
    "@playwright/test": "^1.40.0"
  }
}
```

#### Configure Environment Variables

Create `.env.local` file in the frontend directory:

```bash
# Frontend .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME="Gestione Magazzino"
NEXT_PUBLIC_DEFAULT_LANGUAGE=it
```

#### Run the Frontend Server

```bash
# Start Next.js development server
npm run dev
```

You should see:
```
  ▲ Next.js 14.0.0
  - Local:        http://localhost:3000
  - Ready in 2.5s
```

**Access the application:**
Open your browser and navigate to [http://localhost:3000](http://localhost:3000)

---

### 4. Running the Application

With both servers running, you now have:

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs:** http://localhost:8000/redoc

**Test the full stack:**
1. Open http://localhost:3000
2. Create a new item (e.g., "Olio motore 5W30")
3. Register an IN movement (load stock)
4. Verify the inventory dashboard updates in real-time

---

## Environment Variables

### Backend Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# Database Configuration
DATABASE_URL=postgresql://warehouse_user:dev_password@localhost:5432/inventario_magazzino

# Server Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=true

# CORS Configuration (adjust for production)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Application Settings
APP_NAME="Warehouse Inventory Management API"
API_VERSION=1.0.0
DEBUG=true

# Logging
LOG_LEVEL=INFO

# Security (for future JWT implementation)
SECRET_KEY=your_secret_key_here_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Production `.env` (Render):**
```bash
DATABASE_URL=postgresql://user:password@dpg-xxxxx.oregon-postgres.render.com/inventario_magazzino
CORS_ORIGINS=https://your-frontend.vercel.app
DEBUG=false
LOG_LEVEL=WARNING
```

---

### Frontend Environment Variables

Create `.env.local` in the `frontend` directory:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Application Configuration
NEXT_PUBLIC_APP_NAME="Gestione Magazzino"
NEXT_PUBLIC_DEFAULT_LANGUAGE=it

# Feature Flags (optional)
NEXT_PUBLIC_ENABLE_EXCEL_EXPORT=true
NEXT_PUBLIC_ENABLE_DARK_MODE=false

# Analytics (optional, for production)
# NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
```

**Production `.env.production` (Vercel):**
```bash
NEXT_PUBLIC_API_URL=https://inventario-magazzino.onrender.com
NEXT_PUBLIC_APP_NAME="Gestione Magazzino Officina"
```

---

## Database Migrations

### Using Alembic for Schema Management

Alembic manages database schema evolution through versioned migration scripts.

#### Common Alembic Commands

**Create a new migration:**
```bash
cd backend
alembic revision --autogenerate -m "Add notes column to items table"
```

**Apply migrations (upgrade to latest):**
```bash
alembic upgrade head
```

**Rollback to previous version:**
```bash
alembic downgrade -1
```

**View migration history:**
```bash
alembic history
```

**Check current database version:**
```bash
alembic current
```

**Upgrade to specific revision:**
```bash
alembic upgrade <revision_id>
```

---

### Initial Schema Migration

The initial migration creates the core tables:

**`migrations/versions/001_initial_schema.py`** (example):

```python
"""Initial schema with items and movements tables

Revision ID: 001
Revises:
Create Date: 2025-11-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Enable extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')

    # Create items table
    op.create_table('items',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('unit', sa.String(length=20), nullable=False, server_default='pz'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('min_stock', sa.Numeric(precision=10, scale=3), nullable=False, server_default='0'),
        sa.Column('unit_cost', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('min_stock >= 0', name='chk_items_min_stock_positive'),
        sa.CheckConstraint('unit_cost >= 0', name='chk_items_unit_cost_positive'),
    )

    # Create indexes for items
    op.create_index('idx_items_name_trgm', 'items', ['name'], postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'})
    op.create_index('idx_items_category', 'items', ['category'])
    op.create_index('idx_items_created_at', 'items', ['created_at'])

    # Create movements table
    op.create_table('movements',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('movement_type', sa.String(length=20), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=10, scale=3), nullable=False),
        sa.Column('movement_date', sa.Date(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('unit_cost_override', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("movement_type IN ('IN', 'OUT', 'ADJUSTMENT')", name='chk_movements_type_valid'),
        sa.CheckConstraint('quantity != 0', name='chk_movements_quantity_nonzero'),
    )

    # Create indexes for movements
    op.create_index('idx_movements_item_id', 'movements', ['item_id'])
    op.create_index('idx_movements_timestamp', 'movements', ['timestamp'], postgresql_ops={'timestamp': 'DESC'})
    op.create_index('idx_movements_movement_date', 'movements', ['movement_date'])
    op.create_index('idx_movements_type', 'movements', ['movement_type'])


def downgrade():
    op.drop_table('movements')
    op.drop_table('items')
    op.execute('DROP EXTENSION IF EXISTS "pg_trgm"')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
```

**Apply the migration:**
```bash
alembic upgrade head
```

---

### Seed Data for Testing

Create a script to populate the database with sample data:

**`backend/scripts/seed_data.py`:**

```python
import asyncio
from sqlalchemy import create_engine, text
from datetime import date, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def seed_data():
    with engine.begin() as conn:
        # Insert sample items
        conn.execute(text("""
            INSERT INTO items (name, category, unit, min_stock, unit_cost, notes) VALUES
            ('Olio motore 5W30', 'Lubrificanti', 'lt', 5, 8.50, 'Olio sintetico long life'),
            ('Filtro olio', 'Filtri', 'pz', 10, 4.20, 'Compatibile maggior parte veicoli'),
            ('Pastiglie freno anteriori', 'Freni', 'kit', 3, 35.00, 'Set completo asse anteriore'),
            ('Liquido freni DOT4', 'Liquidi', 'lt', 2, 6.80, 'Specifica DOT4');
        """))

        # Get item IDs
        result = conn.execute(text("SELECT id, name FROM items"))
        items = {name: str(id) for id, name in result}

        # Insert sample movements
        today = date.today()
        conn.execute(text(f"""
            INSERT INTO movements (item_id, movement_type, quantity, movement_date, note) VALUES
            ('{items["Olio motore 5W30"]}', 'IN', 20, '{today - timedelta(days=30)}', 'Carico iniziale magazzino'),
            ('{items["Olio motore 5W30"]}', 'OUT', -3, '{today - timedelta(days=15)}', 'Tagliando Alfa Romeo 159'),
            ('{items["Filtro olio"]}', 'IN', 25, '{today - timedelta(days=60)}', 'Fornitore A - Fattura 123'),
            ('{items["Filtro olio"]}', 'OUT', -18, '{today - timedelta(days=10)}', 'Utilizzo misto officina');
        """))

        print("Seed data inserted successfully!")

if __name__ == "__main__":
    seed_data()
```

**Run the seed script:**
```bash
cd backend
python scripts/seed_data.py
```

---

## Testing

### Backend Tests (pytest)

#### Run All Tests

```bash
cd backend
pytest
```

#### Run Tests with Coverage

```bash
pytest --cov=app --cov-report=html --cov-report=term
```

#### Run Specific Test Files

```bash
# Test items endpoints
pytest tests/test_items.py -v

# Test movements endpoints
pytest tests/test_movements.py -v

# Test database models
pytest tests/test_models.py -v
```

#### Example Test Structure

**`backend/tests/test_items.py`:**

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_item():
    response = client.post("/api/items", json={
        "name": "Test Item",
        "category": "Test Category",
        "unit": "pz",
        "min_stock": 5.0,
        "unit_cost": 10.0
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["stock_quantity"] == 0.0

def test_list_items():
    response = client.get("/api/items")
    assert response.status_code == 200
    assert "items" in response.json()

def test_search_items():
    response = client.get("/api/items?search=olio")
    assert response.status_code == 200
    items = response.json()["items"]
    assert all("olio" in item["name"].lower() for item in items)
```

---

### Frontend Tests

#### Unit Tests (Vitest)

```bash
cd frontend

# Run unit tests
npm run test

# Run with coverage
npm run test:coverage

# Watch mode for development
npm run test:watch
```

#### E2E Tests (Playwright)

**Install Playwright browsers:**
```bash
npx playwright install
```

**Run E2E tests:**
```bash
# Run all E2E tests
npm run test:e2e

# Run in UI mode (interactive)
npm run test:e2e:ui

# Run specific browser
npm run test:e2e -- --project=chromium
```

**Example E2E test (`frontend/tests/e2e/inventory.spec.ts`):**

```typescript
import { test, expect } from '@playwright/test';

test.describe('Inventory Management', () => {
  test('should create new item and register movement', async ({ page }) => {
    await page.goto('http://localhost:3000');

    // Create item
    await page.click('button:has-text("Nuovo Articolo")');
    await page.fill('input[name="name"]', 'Test Item E2E');
    await page.fill('input[name="unit_cost"]', '15.00');
    await page.click('button[type="submit"]');

    // Verify item appears in list
    await expect(page.locator('text=Test Item E2E')).toBeVisible();

    // Register IN movement
    await page.click('button:has-text("Carico")');
    await page.fill('input[name="quantity"]', '50');
    await page.click('button[type="submit"]');

    // Verify stock updates
    await expect(page.locator('text=50.0 pz')).toBeVisible();
  });
});
```

---

## API Documentation

### Accessing Interactive API Documentation

FastAPI provides automatic interactive API documentation through Swagger UI and ReDoc.

#### Swagger UI (Interactive Playground)

**URL:** http://localhost:8000/docs

**Features:**
- Try out API endpoints directly from the browser
- View request/response schemas
- See examples for all endpoints
- Test authentication (future feature)

**Usage:**
1. Navigate to http://localhost:8000/docs
2. Click on any endpoint (e.g., `GET /api/items`)
3. Click "Try it out"
4. Fill in parameters (if any)
5. Click "Execute"
6. View the response

#### ReDoc (Alternative Documentation)

**URL:** http://localhost:8000/redoc

**Features:**
- Clean, three-panel design
- Better for reading documentation
- More detailed schema visualization
- Search functionality

---

### Key API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/items` | List all items with filters |
| `POST` | `/api/items` | Create new item |
| `GET` | `/api/items/{id}` | Get item details |
| `PUT` | `/api/items/{id}` | Update item |
| `DELETE` | `/api/items/{id}` | Delete item (with restrictions) |
| `GET` | `/api/movements` | List movements with filters |
| `POST` | `/api/movements` | Register movement (IN/OUT/ADJUSTMENT) |
| `GET` | `/api/movements/{id}` | Get movement details |
| `GET` | `/api/dashboard/stats` | Get dashboard statistics |
| `GET` | `/api/export/preview` | Get export data (for Excel generation) |
| `GET` | `/api/items/autocomplete/categories` | Get category suggestions |
| `GET` | `/api/items/autocomplete/units` | Get unit suggestions |

---

### API Testing with cURL

**Create an item:**
```bash
curl -X POST http://localhost:8000/api/items \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Olio motore 10W40",
    "category": "Lubrificanti",
    "unit": "lt",
    "min_stock": 5.0,
    "unit_cost": 7.50
  }'
```

**Register IN movement:**
```bash
curl -X POST http://localhost:8000/api/movements \
  -H "Content-Type: application/json" \
  -d '{
    "movement_type": "IN",
    "item_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "quantity": 30.0,
    "movement_date": "2025-11-11",
    "note": "Carico fornitore"
  }'
```

**Get dashboard stats:**
```bash
curl http://localhost:8000/api/dashboard/stats
```

---

## Production Deployment

This section covers deploying the warehouse inventory system to production using free-tier services:

- **Frontend:** Vercel
- **Backend:** Render
- **Database:** Neon PostgreSQL

---

### 1. Database Deployment (Neon)

Neon provides serverless PostgreSQL with a generous free tier (3GB storage).

#### Steps:

1. **Sign up for Neon:**
   - Go to [neon.tech](https://neon.tech)
   - Sign up with GitHub or email
   - Create a new project: "inventario-magazzino"

2. **Configure Database:**
   - Region: Select closest to your users (e.g., Europe Central)
   - PostgreSQL version: 15
   - Database name: `inventario_magazzino`

3. **Get Connection String (CRITICAL - Use Pooled Endpoint):**
   - **IMPORTANT:** For serverless deployments (Render/Vercel), you MUST use the **pooled endpoint** to prevent connection exhaustion
   - In Neon dashboard, copy the connection string with **`.pooler.`** subdomain
   - ✅ **Correct format:** `postgresql://user:password@ep-xxx.pooler.region.aws.neon.tech/inventario_magazzino?sslmode=require`
   - ❌ **Wrong (direct):** `postgresql://user:password@ep-xxx.region.aws.neon.tech/inventario_magazzino?sslmode=require`
   - The `.pooler.` subdomain enables pgBouncer connection pooling, essential for preventing "too many connections" errors on free tier

4. **Enable Extensions:**
   ```bash
   # Note: Use direct endpoint (not .pooler) for admin operations like CREATE EXTENSION
   psql "postgresql://user:password@ep-xxx.region.aws.neon.tech/inventario_magazzino?sslmode=require"

   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   CREATE EXTENSION IF NOT EXISTS "pg_trgm";
   \q
   ```

5. **Run Migrations:**
   ```bash
   # Set DATABASE_URL environment variable with POOLED endpoint
   export DATABASE_URL="postgresql://user:password@ep-xxx.pooler.region.aws.neon.tech/inventario_magazzino?sslmode=require"

   # Apply migrations
   cd backend
   alembic upgrade head
   ```

6. **Configure SQLAlchemy for Serverless (CRITICAL):**

   In `backend/src/db/database.py`, ensure you use `NullPool` to let Neon handle connection pooling:

   ```python
   from sqlalchemy.ext.asyncio import create_async_engine
   from sqlalchemy.pool import NullPool
   import os

   # Use pooled endpoint URL from environment
   DATABASE_URL = os.getenv("DATABASE_URL")  # Must include .pooler. subdomain

   engine = create_async_engine(
       DATABASE_URL,
       poolclass=NullPool,  # CRITICAL: Let Neon pgBouncer handle pooling
       echo=False,
   )
   ```

   **Why NullPool?** Serverless functions create new SQLAlchemy engines frequently. Without `NullPool`, SQLAlchemy would create its own connection pool per engine instance, quickly exhausting Neon's connection limit (100 on free tier).

**Neon Free Tier Limits:**
- 3GB storage
- 1GB egress per month
- Automatic suspension after 300 hours of inactivity (wakes instantly on query)

---

### 2. Backend Deployment (Render)

Render provides free-tier Python hosting with automatic deploys from Git.

#### Steps:

1. **Create Render Account:**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Create Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Branch: `001-warehouse-inventory-system` (or `main`)

3. **Configure Service:**
   ```yaml
   Name: inventario-magazzino-api
   Region: Frankfurt (EU Central)
   Branch: main
   Root Directory: backend
   Runtime: Python 3.11
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port 8000
   Instance Type: Free
   ```

4. **Set Environment Variables:**
   In the Render dashboard, add these environment variables:

   ```
   DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/inventario_magazzino?sslmode=require
   CORS_ORIGINS=https://your-frontend.vercel.app
   DEBUG=false
   LOG_LEVEL=INFO
   ```

5. **Deploy:**
   - Click "Create Web Service"
   - Render will automatically build and deploy
   - First deployment takes ~5-10 minutes

6. **Verify Deployment:**
   - Service URL: `https://inventario-magazzino-api.onrender.com`
   - Test: `curl https://inventario-magazzino-api.onrender.com/api/items`

**Render Free Tier Limits:**
- 512MB RAM
- Service sleeps after 15 minutes of inactivity
- Cold start time: ~2-5 seconds
- 750 hours per month (permanent free)

---

### 3. Frontend Deployment (Vercel)

Vercel provides seamless Next.js deployment with automatic builds.

#### Steps:

1. **Create Vercel Account:**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub

2. **Import Project:**
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Root Directory: `frontend`

3. **Configure Project:**
   ```yaml
   Framework Preset: Next.js
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```

4. **Set Environment Variables:**
   In Vercel project settings → Environment Variables:

   ```
   NEXT_PUBLIC_API_URL=https://inventario-magazzino-api.onrender.com
   NEXT_PUBLIC_APP_NAME="Gestione Magazzino Officina"
   NEXT_PUBLIC_DEFAULT_LANGUAGE=it
   ```

5. **Deploy:**
   - Click "Deploy"
   - Vercel will build and deploy automatically
   - Deployment URL: `https://inventario-magazzino.vercel.app`

6. **Custom Domain (Optional):**
   - Settings → Domains
   - Add your custom domain (e.g., `magazzino.your-shop.com`)
   - Follow DNS configuration instructions

**Vercel Free Tier Limits:**
- 100GB bandwidth per month
- Unlimited static sites
- 100 serverless function executions per day
- Automatic HTTPS
- Global CDN

---

### 4. Post-Deployment Configuration

#### Update CORS on Backend

After deploying the frontend, update the backend CORS configuration:

**Render Environment Variables:**
```
CORS_ORIGINS=https://inventario-magazzino.vercel.app,https://your-custom-domain.com
```

#### Update API URL on Frontend

Redeploy frontend with production API URL:

**Vercel Environment Variables:**
```
NEXT_PUBLIC_API_URL=https://inventario-magazzino-api.onrender.com
```

#### Test Production Deployment

1. Navigate to `https://inventario-magazzino.vercel.app`
2. Create a test item
3. Register a movement
4. Export to Excel
5. Verify data persists across sessions

---

### 5. Monitoring and Maintenance

#### Render Monitoring

- **Logs:** Render Dashboard → Service → Logs tab
- **Metrics:** CPU, memory, response times
- **Health Checks:** Configure at `/health` endpoint

#### Neon Monitoring

- **Database Dashboard:** Query statistics, storage usage
- **Connection Pooling:** Enabled by default with pgBouncer
- **Backups:** Automatic daily backups (retained for 7 days on free tier)

#### Vercel Monitoring

- **Analytics:** Vercel Dashboard → Analytics tab
- **Deployment Logs:** View build and runtime logs
- **Performance:** Core Web Vitals tracking

---

### 6. Scaling Considerations

When you outgrow the free tier:

**Neon Upgrade ($19/month):**
- 10GB storage
- Unlimited egress
- Point-in-time restore

**Render Upgrade ($7/month):**
- 512MB RAM → 2GB RAM
- No sleep (always-on)
- Faster cold starts

**Vercel Pro ($20/month):**
- Analytics
- Password protection
- Team collaboration

---

## Post-Deployment Modifications and Maintenance

Once your application is deployed and in use, you'll need to make modifications, fix bugs, and add features. This section covers best practices for safe production updates.

---

### 1. Development Environment Setup for Production Modifications

**Recommended: Two-Database Strategy**

To safely test changes before production deployment, set up two separate Neon databases:

**Database Setup:**

| Environment | Purpose | Neon Project | Connection |
|-------------|---------|--------------|------------|
| **Development** | Test changes, migrations | `inventario-dev` | Can be destroyed/reset freely |
| **Production** | Live user data | `inventario-prod` | NEVER modify directly |

**Create development database:**
1. Go to [neon.tech](https://neon.tech)
2. Create new project: `inventario-dev`
3. Copy **pooled** connection string: `postgresql://...@ep-xxx.pooler.neon.tech/...`
4. Update `backend/.env.local`:
   ```bash
   DATABASE_URL=postgresql://...@ep-xxx.pooler.neon.tech/inventario_magazzino_dev?sslmode=require
   ```

**Benefit:** Test destructive operations (schema changes, data migrations) on dev database without risk.

---

### 2. Safe Modification Workflow (Feature Branch Strategy)

**Step-by-Step Process:**

#### Step 1: Create Feature Branch

```bash
# Always start from latest main
git checkout main
git pull origin main

# Create descriptive feature branch
git checkout -b fix/inventory-negative-stock-bug
# or
git checkout -b feature/add-supplier-field
```

#### Step 2: Make Changes Locally

```bash
# Work in your local environment
# Backend changes:
cd backend
source venv/bin/activate
uvicorn app.main:app --reload  # Uses dev database

# Frontend changes:
cd frontend
npm run dev
```

**Test thoroughly against development database:**
- Create test items
- Register movements
- Export Excel
- Test edge cases

#### Step 3: Push Branch to GitHub

```bash
git add .
git commit -m "fix: prevent negative stock on concurrent OUT movements"
git push origin fix/inventory-negative-stock-bug
```

#### Step 4: Automatic Preview Deployment

**Vercel automatically creates preview deployment** for every branch push:

```
Preview URL: https://inventario-git-fix-inventory-neg-abc123.vercel.app
```

**Testing preview:**
1. Navigate to preview URL (find in Vercel dashboard or GitHub PR)
2. Preview connects to **production backend** (Render)
3. Test frontend changes without affecting main site
4. Share preview URL with stakeholders for approval

**Note:** Preview uses production backend/database. For isolated testing, temporarily point preview to dev backend via branch-specific Vercel environment variables.

---

### 3. Database Schema Migrations in Production

**CRITICAL:** Always test migrations on development database first.

#### Creating a Migration

**Scenario:** You need to add a `supplier` field to the `items` table.

```bash
cd backend

# 1. Update SQLAlchemy model (backend/src/models/item.py)
class Item(Base):
    __tablename__ = "items"
    # ... existing fields ...
    supplier = Column(String(100), nullable=True)  # New field

# 2. Generate migration with Alembic
alembic revision --autogenerate -m "add supplier field to items"

# 3. Review generated migration file
# Check backend/alembic/versions/abc123_add_supplier_field.py
# Verify upgrade() and downgrade() functions are correct

# 4. Test migration on DEV database
export DATABASE_URL="postgresql://...@ep-xxx.pooler.neon.tech/inventario_magazzino_dev"
alembic upgrade head

# 5. Verify migration succeeded
psql "$DATABASE_URL" -c "\d items"  # Should show 'supplier' column

# 6. Test rollback
alembic downgrade -1
alembic upgrade head  # Re-apply to confirm idempotency
```

#### Applying Migration to Production

**Safe Production Migration Process:**

```bash
# 1. Commit migration file
git add backend/alembic/versions/abc123_add_supplier_field.py
git commit -m "migration: add supplier field to items table"
git push origin fix/inventory-negative-stock-bug

# 2. Merge to main (after code review)
git checkout main
git merge fix/inventory-negative-stock-bug
git push origin main

# 3. Run migration on PRODUCTION database
# Option A: SSH to Render instance (if available)
# Option B: Run locally with production DATABASE_URL (RECOMMENDED)

export DATABASE_URL="postgresql://...@ep-xxx.pooler.neon.tech/inventario_magazzino_prod"
cd backend
alembic upgrade head

# 4. Verify migration
psql "$DATABASE_URL" -c "SELECT supplier FROM items LIMIT 1;"
# Should return NULL for existing rows (new column)

# 5. Deploy updated code
# Render auto-deploys on git push to main
# Backend will now use new 'supplier' field
```

**Migration Best Practices:**
- ✅ Always add new columns as `nullable=True` for backward compatibility
- ✅ Test both `upgrade` and `downgrade` on dev database
- ✅ Run migrations **before** deploying code that uses new schema
- ✅ For complex migrations, use [blue-green deployment](https://en.wikipedia.org/wiki/Blue-green_deployment)
- ❌ Never run destructive migrations (DROP COLUMN, DROP TABLE) without backup

---

### 4. Deployment Timeline and Downtime

**Expected Deployment Times:**

| Component | Deployment Time | Downtime | Notes |
|-----------|----------------|----------|-------|
| **Frontend (Vercel)** | 30-60 seconds | **0 seconds** | Atomic deployment with instant switchover |
| **Backend (Render)** | 2-5 minutes | **~2-3 minutes** | Service restarts, free tier cold start |
| **Database (Neon)** | N/A (always-on) | **0 seconds** | Serverless, no deployment needed |
| **Migrations** | Seconds to minutes | **Depends on migration** | Schema-only migrations = minimal downtime |

**Minimizing Downtime:**

**Strategy 1: Deploy During Off-Hours**
```bash
# Schedule deployments when shop is closed (e.g., evenings, weekends)
# Example: Deploy at 8 PM when no one is using the system
```

**Strategy 2: Database Migrations First, Code Second**
```bash
# 1. Run migration (adds new column, backward compatible)
alembic upgrade head

# 2. Deploy backend code (can use new column, old code ignores it)
git push origin main

# Result: Zero effective downtime for users
```

**Strategy 3: Upgrade to Render Standard ($7/month)**
- Eliminates cold starts
- Zero-downtime deployments with health checks
- Background workers for long-running tasks

---

### 5. Rollback Strategy

**When Things Go Wrong:**

#### Frontend Rollback (Vercel)

**Option A: Instant Rollback via Vercel Dashboard**
1. Go to Vercel dashboard → Deployments
2. Find previous working deployment
3. Click "..." → "Promote to Production"
4. **Rollback time:** ~10 seconds

**Option B: Git Revert**
```bash
git revert HEAD
git push origin main
# Vercel auto-deploys reverted version (~1 minute)
```

#### Backend Rollback (Render)

**Option A: Redeploy Previous Commit**
1. Render dashboard → Manual Deploy tab
2. Select previous commit SHA
3. Click "Deploy"
4. **Rollback time:** ~3-5 minutes (rebuild required)

**Option B: Git Revert**
```bash
git revert HEAD
git push origin main
# Render auto-deploys (~3-5 minutes)
```

#### Database Migration Rollback

```bash
# Rollback last migration
export DATABASE_URL="postgresql://...production..."
cd backend
alembic downgrade -1

# Verify rollback
alembic current
```

**⚠️ Warning:** Rollback is only safe if:
- Migration was just applied (no user data in new columns)
- Downgrade script properly reverses all changes
- No dependent code is currently deployed

---

### 6. Monitoring Production Health

#### Setting Up UptimeRobot (Free Health Checks)

**Purpose:** Keep Render backend warm, detect downtime.

**Setup:**
1. Sign up at [uptimerobot.com](https://uptimerobot.com) (free)
2. Create new monitor:
   - **Type:** HTTP(s)
   - **URL:** `https://inventario-magazzino-api.onrender.com/health`
   - **Interval:** 5 minutes (free tier)
   - **Alert Contacts:** Your email
3. Backend stays warm = no cold starts during business hours

**Health Endpoint (backend/app/main.py):**
```python
from datetime import datetime
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected"  # Optional: test DB connection
    }
```

#### Viewing Production Logs

**Render Logs:**
```bash
# View in dashboard: Render → Service → Logs tab
# Last 7 days available on free tier

# Search for errors
# Dashboard → Logs → Filter: "ERROR" or "500"
```

**Vercel Logs:**
```bash
# Install Vercel CLI
npm install -g vercel

# View logs
vercel logs inventario-magazzino

# Real-time logs
vercel logs inventario-magazzino --follow
```

**Neon Query Logs:**
- Neon dashboard → Monitoring tab
- View slow queries, connection count, storage usage

---

### 7. Common Production Scenarios

#### Scenario 1: Fix Critical Bug (Fast Path)

```bash
# 1. Create hotfix branch
git checkout -b hotfix/stock-calculation-error

# 2. Fix bug, test locally
# ... make changes ...

# 3. Push directly to main (skip preview for critical fixes)
git add .
git commit -m "hotfix: fix stock calculation rounding error"
git push origin hotfix/stock-calculation-error

# 4. Merge to main immediately
gh pr create --title "HOTFIX: Stock calculation error" --web
# Merge PR via GitHub

# 5. Monitor deployment
# Vercel: ~1 minute
# Render: ~3-5 minutes

# 6. Verify fix in production
curl https://inventario-magazzino-api.onrender.com/api/dashboard/stats
```

**Total time to production:** ~5-10 minutes

---

#### Scenario 2: Add New Feature (Standard Path)

```bash
# 1. Create feature branch
git checkout -b feature/add-barcode-scanner

# 2. Develop feature (may take days/weeks)
# ... work on feature ...

# 3. Test on development database
export DATABASE_URL="<dev-database>"
# ... test thoroughly ...

# 4. Create migration if needed
alembic revision --autogenerate -m "add barcode column to items"
alembic upgrade head  # Test on dev DB

# 5. Push to GitHub
git push origin feature/add-barcode-scanner

# 6. Create pull request
gh pr create --title "Add barcode scanner support" --web

# 7. Review preview deployment
# Vercel creates: https://inventario-git-feature-add-barcode-abc.vercel.app
# Test thoroughly

# 8. Merge to main after approval
# GitHub → Merge pull request

# 9. Run migration on production
export DATABASE_URL="<prod-database>"
alembic upgrade head

# 10. Verify production deployment
# Check Vercel + Render dashboards
```

**Total time to production:** After approval, ~5 minutes deploy time

---

#### Scenario 3: Update Dependencies (Security Patches)

```bash
# Backend (Python)
cd backend
pip list --outdated
pip install --upgrade fastapi sqlalchemy  # Update specific packages
pip freeze > requirements.txt

# Frontend (Node.js)
cd frontend
npm outdated
npm update  # Updates within semver ranges
# or for major versions:
npm install react@latest next@latest

# Test locally
npm run build  # Ensure build succeeds
pytest  # Run backend tests

# Deploy
git add requirements.txt package.json package-lock.json
git commit -m "chore: update dependencies for security patches"
git push origin main
```

---

### 8. Security Considerations for Public Deployment

**⚠️ Authentication Decision Point:**

Currently, the system has **no authentication** (single-user assumption per Constitution IV). This is acceptable **only if**:

✅ **Safe scenarios:**
- Deployed on **private network** (office LAN only, no internet access)
- **Firewall protected** (IP whitelist, VPN-only access)
- **Single authorized user** with physical access control

❌ **Unsafe scenarios (require authentication):**
- Vercel URL is **publicly accessible** on internet
- Multiple workshop locations sharing same system
- Any remote access requirements

**If deploying publicly, implement minimal authentication:**

**Option A: Vercel Password Protection (Easiest)**
- Upgrade to Vercel Pro ($20/month)
- Enable password protection in deployment settings
- Share password only with authorized users

**Option B: Google OAuth (Free)**
```python
# backend: Add Google OAuth with single authorized email whitelist
AUTHORIZED_EMAILS = ["owner@workshop.com"]

# Reject all other login attempts
```

**Option C: Simple API Key (Quick Fix)**
```python
# backend/app/main.py
from fastapi import Header, HTTPException

API_KEY = os.getenv("API_KEY")  # Set in Render environment

@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    if request.url.path.startswith("/api"):
        key = request.headers.get("X-API-Key")
        if key != API_KEY:
            raise HTTPException(401, "Invalid API key")
    return await call_next(request)
```

**Current Recommendation:** Document in deployment README that system is intended for private network deployment. If user needs public access, add authentication before going live.

---

### 9. Backup and Disaster Recovery

**Neon Automatic Backups:**
- **Free tier:** 7 days of backups, retained automatically
- **Recovery:** Neon dashboard → Restore → Select timestamp

**Manual Backup Before Major Changes:**
```bash
# Before running destructive migration or data transformation
pg_dump "postgresql://...@ep-xxx.pooler.neon.tech/inventario_magazzino_prod" > backup_$(date +%Y%m%d).sql

# Restore if needed
psql "postgresql://...@ep-xxx.pooler.neon.tech/inventario_magazzino_prod" < backup_20251111.sql
```

**Export Critical Data:**
```bash
# Export all items and movements to JSON (can be re-imported)
curl https://inventario-magazzino-api.onrender.com/api/export/preview > backup.json
```

---

### 10. Workflow Summary Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ Production Modification Workflow                            │
└─────────────────────────────────────────────────────────────┘

1. LOCAL DEVELOPMENT
   ├─ git checkout -b feature/my-feature
   ├─ Edit code
   ├─ Test against DEV database
   └─ git push origin feature/my-feature
         │
         ▼
2. PREVIEW DEPLOYMENT (Automatic)
   ├─ Vercel creates preview URL
   ├─ Test preview deployment
   └─ Share with stakeholders
         │
         ▼
3. CODE REVIEW & APPROVAL
   ├─ Create GitHub Pull Request
   ├─ Review code changes
   └─ Approve merge
         │
         ▼
4. DATABASE MIGRATION (If Needed)
   ├─ Test migration on DEV database
   └─ Run migration on PROD database
         │
         ▼
5. DEPLOY TO PRODUCTION
   ├─ git merge to main
   ├─ git push origin main
   ├─ Vercel auto-deploys frontend (~1 min)
   ├─ Render auto-deploys backend (~3-5 min)
   └─ Verify production health
         │
         ▼
6. MONITOR & ROLLBACK (If Issues)
   ├─ Check logs (Render/Vercel/Neon)
   ├─ Test production endpoints
   └─ Rollback if critical issues detected

Total Time: 5-10 minutes (after approval)
Downtime: ~2-3 minutes (backend only, frontend 0 downtime)
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Database Connection Errors

**Error:** `sqlalchemy.exc.OperationalError: could not connect to server`

**Solutions:**
```bash
# Check PostgreSQL is running
# Docker:
docker ps | grep postgres

# Local installation:
# macOS:
brew services list | grep postgresql
# Linux:
sudo systemctl status postgresql

# Verify connection string
psql "postgresql://warehouse_user:dev_password@localhost:5432/inventario_magazzino"

# Check firewall rules (if using remote database)
telnet your-db-host 5432
```

---

#### 2. Alembic Migration Conflicts

**Error:** `alembic.util.exc.CommandError: Target database is not up to date`

**Solutions:**
```bash
# Check current version
alembic current

# View pending migrations
alembic history

# Force stamp to specific revision (if database is manually synced)
alembic stamp head

# Rollback and re-apply
alembic downgrade -1
alembic upgrade head
```

---

#### 3. CORS Errors in Frontend

**Error:** `Access to fetch at 'http://localhost:8000/api/items' has been blocked by CORS policy`

**Solutions:**

**Backend (`backend/app/main.py`):**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Verify CORS headers:**
```bash
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     http://localhost:8000/api/items -v
```

---

#### 4. Frontend Build Errors

**Error:** `Module not found: Can't resolve 'xlsx'` (or similar dependency errors)

**Solutions:**
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Clear Next.js cache
rm -rf .next

# Rebuild
npm run build
```

---

#### 5. Port Already in Use

**Error:** `Address already in use: bind: address already in use`

**Solutions:**
```bash
# Find process using port 8000
# macOS/Linux:
lsof -i :8000
# Windows:
netstat -ano | findstr :8000

# Kill the process
# macOS/Linux:
kill -9 <PID>
# Windows:
taskkill /PID <PID> /F

# Or use different port
uvicorn app.main:app --port 8001
```

---

#### 6. Render Cold Starts

**Issue:** First request after inactivity takes 5+ seconds

**Solutions:**
- Use [UptimeRobot](https://uptimerobot.com) to ping your backend every 10 minutes (free service)
- Add a `/health` endpoint for health checks
- Upgrade to Render paid plan for always-on instances

**Health check endpoint:**
```python
# backend/app/main.py
@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
```

---

#### 7. PostgreSQL Extension Missing

**Error:** `type "uuid" does not exist`

**Solution:**
```bash
# Connect to database
psql -h localhost -U warehouse_user -d inventario_magazzino

# Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

# Verify
SELECT * FROM pg_extension;
\q
```

---

#### 8. Excel Export Not Working

**Error:** Excel file downloads but cannot be opened

**Solutions:**

**Check SheetJS (xlsx) version:**
```bash
cd frontend
npm list xlsx
```

**Verify MIME type (SheetJS handles this automatically):**
```typescript
// frontend/src/services/exportExcel.ts
import * as XLSX from 'xlsx';

// SheetJS writeFile handles MIME type automatically
XLSX.writeFile(workbook, 'export.xlsx');
```

**For manual blob creation (advanced):**
```typescript
import * as XLSX from 'xlsx';

const workbook = XLSX.utils.book_new();
// ... add sheets ...
const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
const blob = new Blob([excelBuffer], {
  type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
});
```

**Test export manually:**
```bash
# Download from API
curl http://localhost:8000/api/export/preview > export.json

# Verify JSON is valid
cat export.json | jq .
```

---

## Useful Commands

### Development Workflow

```bash
# Start all services (backend + frontend + database)
# Terminal 1: Database
docker-compose up postgres

# Terminal 2: Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 3: Frontend
cd frontend
npm run dev
```

---

### Database Management

```bash
# Backup database
pg_dump -h localhost -U warehouse_user inventario_magazzino > backup.sql

# Restore database
psql -h localhost -U warehouse_user inventario_magazzino < backup.sql

# Reset database (WARNING: deletes all data)
psql -h localhost -U warehouse_user -d postgres -c "DROP DATABASE inventario_magazzino;"
psql -h localhost -U warehouse_user -d postgres -c "CREATE DATABASE inventario_magazzino;"
alembic upgrade head
python scripts/seed_data.py
```

---

### Testing

```bash
# Backend: Run all tests with coverage
cd backend
pytest --cov=app --cov-report=html

# Frontend: Run all tests
cd frontend
npm run test && npm run test:e2e

# Lint and format code
# Backend:
cd backend
black app/
flake8 app/

# Frontend:
cd frontend
npm run lint
npm run format
```

---

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature-name

# Commit changes
git add .
git commit -m "feat: add new feature description"

# Push to remote
git push origin feature/new-feature-name

# Create pull request (use GitHub CLI)
gh pr create --title "Add new feature" --body "Description"
```

---

### Production Deployment

```bash
# Deploy backend to Render (automatic on git push)
git push origin main

# Deploy frontend to Vercel (automatic on git push)
git push origin main

# Manual deployment (Vercel CLI)
cd frontend
vercel --prod

# Check deployment status
vercel ls
```

---

### Logs and Debugging

```bash
# Backend logs (local)
tail -f backend/logs/app.log

# Backend logs (Render)
# View in Render Dashboard or use CLI:
render logs -s inventario-magazzino-api

# Frontend logs (Vercel)
vercel logs inventario-magazzino

# Database logs (Neon)
# View in Neon Dashboard → Monitoring tab
```

---

### Quick Reference

| Task | Command |
|------|---------|
| Start backend | `uvicorn app.main:app --reload` |
| Start frontend | `npm run dev` |
| Run migrations | `alembic upgrade head` |
| Create migration | `alembic revision --autogenerate -m "description"` |
| Run backend tests | `pytest` |
| Run frontend tests | `npm run test` |
| Seed database | `python scripts/seed_data.py` |
| Check API docs | Visit http://localhost:8000/docs |
| Build frontend | `npm run build` |
| Lint code | `npm run lint` |
| Format code | `black app/` (backend), `npm run format` (frontend) |

---

## Additional Resources

### Documentation Links

- **FastAPI Documentation:** [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **SQLAlchemy 2.0 Docs:** [docs.sqlalchemy.org](https://docs.sqlalchemy.org)
- **Alembic Documentation:** [alembic.sqlalchemy.org](https://alembic.sqlalchemy.org)
- **Next.js Documentation:** [nextjs.org/docs](https://nextjs.org/docs)
- **PostgreSQL Documentation:** [postgresql.org/docs](https://www.postgresql.org/docs/)
- **SheetJS Documentation:** [docs.sheetjs.com](https://docs.sheetjs.com)

---

### Related Project Documents

- **Feature Specification:** [`specs/001-warehouse-inventory-system/spec.md`](/Users/francescocarlesi/Downloads/Progetti Python/inventario_magazzino/specs/001-warehouse-inventory-system/spec.md)
- **Data Model:** [`specs/001-warehouse-inventory-system/data-model.md`](/Users/francescocarlesi/Downloads/Progetti Python/inventario_magazzino/specs/001-warehouse-inventory-system/data-model.md)
- **Research Notes:** [`specs/001-warehouse-inventory-system/research.md`](/Users/francescocarlesi/Downloads/Progetti Python/inventario_magazzino/specs/001-warehouse-inventory-system/research.md)
- **API Contract:** [`specs/001-warehouse-inventory-system/contracts/openapi.yaml`](/Users/francescocarlesi/Downloads/Progetti Python/inventario_magazzino/specs/001-warehouse-inventory-system/contracts/openapi.yaml)

---

## Support and Contributing

### Getting Help

- **GitHub Issues:** Report bugs or request features
- **Discussions:** Ask questions in GitHub Discussions
- **Email:** support@example.com

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

**Version:** 1.0
**Last Updated:** 2025-11-11
**Maintainer:** Development Team
