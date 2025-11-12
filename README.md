# 🔧 Sistema di Gestione Magazzino Officina

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg)](https://www.typescriptlang.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

Sistema web completo per la gestione dell'inventario di un'officina auto. Traccia movimenti di magazzino (carico/scarico/rettifiche), visualizza giacenze in tempo reale, genera export Excel e supporta gestione completa articoli.

**🇮🇹 Completamente in italiano** - Interfaccia, messaggi di errore, validazioni e documentazione localizzati.

---

## ✨ Caratteristiche

### 📊 Dashboard Inventario
- **Visualizzazione real-time** delle giacenze con calcolo automatico
- **Statistiche istantanee**: valore totale magazzino, articoli sotto scorta
- **Ricerca e filtri**: per nome, categoria, stato sotto-scorta
- **Evidenziazione visiva** articoli sotto scorta minima

### 📦 Gestione Articoli
- **CRUD completo**: crea, modifica, elimina articoli
- **Autocomplete intelligente** per categorie e unità di misura
- **Validazione giacenza**: impedisce eliminazione con stock > 0 o movimenti recenti
- **Campi personalizzabili**: categoria, unità, note, scorta minima, costo unitario

### 📝 Registrazione Movimenti
- **Carico (IN)**: registra entrate merce con costo unitario opzionale
- **Scarico (OUT)**: scarica materiale con validazione giacenza disponibile
- **Rettifica (ADJUSTMENT)**: correggi giacenze dopo conteggio fisico
- **Conferme obbligatorie** per operazioni critiche
- **Note e timestamp** automatici per audit trail completo

### 📈 Storico Movimenti
- **Visualizzazione completa** con filtri per data, articolo, tipo
- **Paginazione** per grandi volumi di dati
- **Export Excel** ultimi 12 mesi con formattazione italiana

### 📊 Export Excel
- **Due fogli**: Inventario + Movimenti (ultimi 12 mesi)
- **Formattazione italiana**: date DD/MM/YYYY, numeri 1.234,56, valute €X.XXX,XX
- **Download automatico** generato lato client (SheetJS)
- **Pronto per archiviazione** e invio al commercialista

---

## 🛠️ Stack Tecnologico

### Backend
- **FastAPI** 0.104+ - Web framework moderno e veloce
- **SQLAlchemy** 2.x - ORM con supporto async
- **Alembic** - Database migrations
- **PostgreSQL** 15+ - Database relazionale (Neon cloud)
- **Pydantic** - Validazione dati e schemas

### Frontend
- **Next.js** 14+ - React framework con SSR
- **TypeScript** 5.x - Type safety
- **TailwindCSS** - Utility-first CSS
- **SWR** - Data fetching e caching
- **SheetJS (xlsx)** - Excel generation
- **React Number Format** - Input numerico localizzato

### Deployment
- **Render** - Backend hosting
- **Vercel** - Frontend hosting
- **Neon** - PostgreSQL managed database

---

## 🚀 Quick Start

### Prerequisiti
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (o account Neon gratuito)

### Installazione

#### 1. Clona il repository
```bash
git clone https://github.com/fracarlesi/inventario_magazzino.git
cd inventario_magazzino
git checkout 001-warehouse-inventory-system
```

#### 2. Setup Backend
```bash
cd backend

# Crea virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installa dipendenze
pip install -r requirements.txt

# Configura environment
cp .env.example .env
# Modifica .env con le tue credenziali database
```

**⚠️ IMPORTANTE**: Usa l'endpoint **pooled** di Neon (`.pooler.neon.tech`) nel `DATABASE_URL`!

```bash
# Esegui migrations
alembic upgrade head

# [Opzionale] Seed dati di test (10 articoli + 20 movimenti)
python -m scripts.seed_data

# Avvia server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend disponibile su: http://localhost:8000
📚 API Docs: http://localhost:8000/docs

#### 3. Setup Frontend
```bash
cd frontend

# Installa dipendenze
npm install
# oppure: yarn install

# Configura environment
cp .env.example .env.local
# Modifica .env.local se il backend non è su localhost:8000

# Avvia development server
npm run dev
# oppure: yarn dev
```

✅ Frontend disponibile su: http://localhost:3000

---

## 📁 Struttura Progetto

```
inventario_magazzino/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── api/               # REST endpoints
│   │   │   ├── items.py       # Gestione articoli
│   │   │   ├── movements.py   # Registrazione movimenti
│   │   │   ├── dashboard.py   # Statistiche
│   │   │   └── export.py      # Export Excel
│   │   ├── models/            # SQLAlchemy models + schemas
│   │   ├── services/          # Business logic
│   │   └── db/                # Database connection
│   ├── alembic/               # Database migrations
│   ├── scripts/               # Utility scripts (seed data)
│   ├── tests/                 # Unit + integration tests
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Next.js pages (routing)
│   │   ├── services/          # API client + Excel generation
│   │   ├── types/             # TypeScript types
│   │   └── i18n/              # Localizzazione italiana
│   ├── tests/                 # Component + E2E tests
│   └── package.json           # Node dependencies
│
├── specs/                      # Documentazione progetto
│   └── 001-warehouse-inventory-system/
│       ├── spec.md            # Specifica funzionale
│       ├── plan.md            # Piano implementazione
│       ├── data-model.md      # Schema database
│       ├── tasks.md           # Task breakdown (90/102 ✓)
│       └── contracts/         # OpenAPI spec
│
├── SETUP.md                   # Guida setup dettagliata
└── README.md                  # Questo file
```

---

## 📖 Documentazione

- **[SETUP.md](SETUP.md)** - Guida completa setup e troubleshooting
- **[Specification](specs/001-warehouse-inventory-system/spec.md)** - Requisiti funzionali e user stories
- **[Implementation Plan](specs/001-warehouse-inventory-system/plan.md)** - Architettura e decisioni tecniche
- **[Data Model](specs/001-warehouse-inventory-system/data-model.md)** - Schema database e relazioni
- **[Tasks](specs/001-warehouse-inventory-system/tasks.md)** - Task breakdown dettagliato (90/102 completati)
- **[API Contracts](specs/001-warehouse-inventory-system/contracts/openapi.yaml)** - OpenAPI 3.0 spec

---

## 🧪 Testing

### Backend
```bash
cd backend
pytest                          # Run all tests
pytest tests/unit              # Unit tests only
pytest tests/integration       # Integration tests only
pytest --cov                   # With coverage report
```

### Frontend
```bash
cd frontend
npm run test                   # Vitest unit tests
npm run test:coverage          # With coverage
npm run test:e2e              # Playwright E2E tests
npm run test:e2e:ui           # E2E with UI
```

---

## 🎯 Funzionalità Completate

- ✅ **US1 (P1)** - Dashboard inventario con filtri e ricerca
- ✅ **US2 (P2)** - Registrazione movimenti IN (carico merce)
- ✅ **US3 (P3)** - Registrazione movimenti OUT (scarico merce)
- ✅ **US4 (P4)** - Gestione CRUD articoli
- ✅ **US5 (P5)** - Storico movimenti con filtri
- ✅ **US6 (P6)** - Export Excel ultimi 12 mesi
- ✅ **US7 (P4)** - Rettifiche inventario (ADJUSTMENT)

**Task completati**: 90/102 (~88%)

---

## 🚧 Roadmap

### In Sviluppo
- [ ] Loading states e skeleton loaders
- [ ] Performance optimization (caching)
- [ ] Test coverage > 80%

### Deployment
- [ ] Setup Neon database
- [ ] Deploy backend su Render
- [ ] Deploy frontend su Vercel
- [ ] Configurazione production CORS

### Future Features
- [ ] Autenticazione multi-utente
- [ ] Reportistica avanzata
- [ ] Notifiche email automatiche
- [ ] Lettore barcode/QR
- [ ] Grafici e analytics
- [ ] App mobile (React Native)

---

## 🤝 Contribuire

Questo è un progetto di collaborazione familiare, ma accettiamo contributi esterni!

### Workflow
1. Fork il repository
2. Crea feature branch: `git checkout -b feature/nome-feature`
3. Commit: `git commit -m 'Add: descrizione'`
4. Push: `git push origin feature/nome-feature`
5. Apri una Pull Request

### Convenzioni
- **Commit messages**: In italiano, usando prefissi (`Add:`, `Fix:`, `Update:`, `Refactor:`)
- **Code style**: Black (Python), Prettier (TypeScript)
- **Localizzazione**: Tutto in italiano (UI, error messages)

### Setup pre-commit
```bash
# Backend
cd backend
pip install black flake8
black src/
flake8 src/

# Frontend
cd frontend
npm run lint
npm run format
```

---

## 📝 License

Questo progetto è rilasciato sotto licenza **MIT**. Vedi [LICENSE](LICENSE) per dettagli.

---

## 👥 Team

- **Francesco Carlesi** ([@fracarlesi](https://github.com/fracarlesi)) - Project Lead & Development
- **Collaboratori** - Tuo fratello e altri contributor

---

## 🙏 Ringraziamenti

- Built with [Claude Code](https://claude.com/claude-code) 🤖
- Stack tecnologico: FastAPI, Next.js, PostgreSQL, TailwindCSS
- Hosting: Render, Vercel, Neon

---

## 📧 Contatti

- **Issues**: [GitHub Issues](https://github.com/fracarlesi/inventario_magazzino/issues)
- **Discussions**: [GitHub Discussions](https://github.com/fracarlesi/inventario_magazzino/discussions)

---

**Made with ❤️ in Italy 🇮🇹**
