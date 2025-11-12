# Setup Guide - Sistema di Gestione Magazzino

Quick setup guide for local development.

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm/yarn
- PostgreSQL 15+ (or Neon account for cloud database)

## Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

   **Important**: Use Neon pooled endpoint (`.pooler.neon.tech`) not direct endpoint!

5. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

6. **[Optional] Seed test data**:
   ```bash
   python -m scripts.seed_data
   ```

7. **Start backend server**:
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Backend will be available at: http://localhost:8000
   API docs: http://localhost:8000/docs

## Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env.local
   # Edit .env.local if your backend is not on localhost:8000
   ```

4. **Start frontend development server**:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

   Frontend will be available at: http://localhost:3000

## Verify Installation

1. Open http://localhost:3000 in your browser
2. You should see the dashboard with:
   - Statistics panel (total value, under-stock count, etc.)
   - Inventory table
   - Action buttons (Nuovo Articolo, Carico, Scarico, Rettifica, Esporta Excel)

3. If you seeded data, you should see 10 items with various stock levels

## Testing Features

### Create an Item
1. Click "Nuovo Articolo"
2. Fill in: Name, Category, Unit, Min Stock, Unit Cost
3. Save

### Register IN Movement
1. Click "Carico (IN)"
2. Select an item
3. Enter quantity and optional cost override
4. Save → Stock should increase

### Register OUT Movement
1. Click "Scarico (OUT)"
2. Select an item with stock > 0
3. Enter quantity
4. Confirm → Stock should decrease

### Register ADJUSTMENT
1. Click "Rettifica"
2. Select an item
3. Enter target stock (different from current)
4. Add mandatory note explaining the adjustment
5. Save → Stock should be corrected

### Export Excel
1. Click "Esporta Excel (ultimi 12 mesi)"
2. Browser should download `magazzino_YYYYMMDD.xlsx`
3. Open in Excel/LibreOffice to verify:
   - "Inventario" sheet with all items
   - "Movimenti_ultimi_12_mesi" sheet with movements
   - Italian formatting (dates DD/MM/YYYY, numbers with comma separator)

## Troubleshooting

### Backend won't start
- Check DATABASE_URL in backend/.env
- Verify PostgreSQL is running
- Run `alembic upgrade head` to ensure migrations are applied

### Frontend won't connect to backend
- Check NEXT_PUBLIC_API_URL in frontend/.env.local
- Verify backend is running on http://localhost:8000
- Check CORS_ORIGINS in backend/.env includes http://localhost:3000

### Database connection errors
- If using Neon: Ensure you're using the POOLED endpoint (.pooler.neon.tech)
- Check credentials and network connectivity
- Verify SSL mode is set to `?sslmode=require` in DATABASE_URL

### Excel export doesn't work
- Check browser console for errors
- Verify backend /api/export/preview endpoint is accessible
- Ensure xlsx library is installed in frontend (npm install xlsx)

## Next Steps

- Configure production database (Neon)
- Deploy backend to Render
- Deploy frontend to Vercel
- Update CORS_ORIGINS and API URLs for production
- Run Italian locale validation checklist (frontend/tests/locale-validation.md)

## Useful Commands

### Backend
```bash
# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Create new migration
alembic revision --autogenerate -m "description"

# Run tests
pytest

# Code formatting
black src/
flake8 src/
```

### Frontend
```bash
# Development
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Linting
npm run lint

# Type checking
tsc --noEmit
```

## Documentation

- [Specification](specs/001-warehouse-inventory-system/spec.md)
- [Implementation Plan](specs/001-warehouse-inventory-system/plan.md)
- [Data Model](specs/001-warehouse-inventory-system/data-model.md)
- [API Contracts](specs/001-warehouse-inventory-system/contracts/)
- [Tasks](specs/001-warehouse-inventory-system/tasks.md)
