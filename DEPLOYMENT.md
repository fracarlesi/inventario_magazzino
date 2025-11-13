# Guida al Deployment in Produzione

Sistema di Gestione Inventario Magazzino - Documentazione per il deployment su Vercel (Frontend) e Render (Backend)

## Indice

1. [Architettura Produzione](#architettura-produzione)
2. [Database](#database)
3. [Backend Deployment (Render)](#backend-deployment-render)
4. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
5. [Verifica e Testing](#verifica-e-testing)
6. [Troubleshooting](#troubleshooting)

---

## Architettura Produzione

### Stack Tecnologico
- **Frontend**: Next.js 14+ su Vercel
- **Backend**: FastAPI (Python 3.11) su Render (Docker)
- **Database**: PostgreSQL su Neon (serverless)

### URL Produzione
- **Frontend**: https://inventario-magazzino.vercel.app
- **Backend API**: https://inventario-magazzino-backend.onrender.com
- **Database**: Neon PostgreSQL (pooled connection)

---

## Database

### Setup Neon PostgreSQL

1. **Crea Database su Neon.tech**
   - Nome: `inventario_magazzino`
   - Region: Scegli la più vicina geograficamente
   - Postgres version: 15+

2. **Ottieni Connection String**
   ```
   postgresql://user:password@ep-xxx.pooler.region.aws.neon.tech:5432/inventario_magazzino
   ```

   **IMPORTANTE**: Usa sempre il pooled endpoint (contiene `.pooler.`) per evitare l'esaurimento delle connessioni in ambienti serverless.

3. **Migrazioni Database**
   Le migrazioni vengono eseguite automaticamente durante il deployment del backend tramite Alembic.

---

## Backend Deployment (Render)

### 1. Configurazione Servizio

**Tipo**: Web Service
**Repository**: GitHub - fracarlesi/inventario_magazzino
**Branch**: 001-warehouse-inventory-system
**Root Directory**: backend
**Runtime**: Docker

### 2. Build Settings

**Dockerfile**: `backend/Dockerfile`
```dockerfile
# Multi-stage build per ottimizzare dimensioni immagine
FROM python:3.11-slim as builder
# ... (vedi Dockerfile completo)
```

**Build Command**: Automatico (usa Dockerfile)
**Start Command**:
```bash
uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

### 3. Environment Variables

Configura le seguenti variabili d'ambiente su Render:

| Variabile | Valore | Descrizione |
|-----------|--------|-------------|
| `DATABASE_URL` | `postgresql://user:pass@ep-xxx.pooler...` | Connection string Neon (pooled) |
| `CORS_ORIGINS` | `https://inventario-magazzino.vercel.app,http://localhost:3000` | Domini autorizzati per CORS |
| `DEBUG` | `false` | Disabilita debug in produzione |

**IMPORTANTE**:
- Il DATABASE_URL deve usare il pooled endpoint di Neon (contiene `.pooler.`)
- CORS_ORIGINS deve includere il dominio Vercel di produzione

### 4. Health Check

Endpoint: `/health`
Configurato nel Dockerfile:
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"
```

### 5. Deploy

1. Vai su [Render Dashboard](https://dashboard.render.com)
2. Crea nuovo Web Service
3. Connetti repository GitHub
4. Configura branch e directory root
5. Aggiungi environment variables
6. Deploy!

---

## Frontend Deployment (Vercel)

### 1. Configurazione Progetto

**Repository**: GitHub - fracarlesi/inventario_magazzino
**Branch Produzione**: 001-warehouse-inventory-system
**Root Directory**: frontend
**Framework**: Next.js
**Build Command**: `npm run build`
**Output Directory**: .next

### 2. Environment Variables

Configura su Vercel Settings > Environment Variables:

| Variabile | Valore | Ambiente |
|-----------|--------|----------|
| `NEXT_PUBLIC_API_URL` | `https://inventario-magazzino-backend.onrender.com/api` | Production, Preview, Development |

**IMPORTANTE**:
- Il valore deve includere `/api` alla fine
- NEXT_PUBLIC_ rende la variabile disponibile nel browser
- Applica a tutti gli ambienti (Production, Preview, Development)

### 3. Build Settings

```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install"
}
```

### 4. Deployment

#### Automatic Deployment
Ogni push al branch `001-warehouse-inventory-system` triggera un deployment automatico.

#### Manual Deployment
1. Vai su [Vercel Dashboard](https://vercel.com)
2. Seleziona progetto `inventario-magazzino`
3. Tab "Deployments"
4. Click "Redeploy" sul deployment desiderato

#### Branch Production
Settings > Git > Production Branch: `001-warehouse-inventory-system`

---

## Verifica e Testing

### 1. Verifica Backend

```bash
# Health check
curl https://inventario-magazzino-backend.onrender.com/health

# Response atteso:
{
  "status": "ok",
  "app": "Warehouse Inventory Management API",
  "version": "1.0.0"
}
```

```bash
# Test API endpoint
curl https://inventario-magazzino-backend.onrender.com/api/items

# Response atteso: array di items JSON
```

### 2. Verifica Frontend

1. Apri https://inventario-magazzino.vercel.app
2. Verifica che la dashboard carichi i dati:
   - Valore Totale Magazzino
   - Numero Articoli
   - Tabella inventario popolata
3. Nessun errore CORS nella console

### 3. Test End-to-End

1. **Visualizzazione Dashboard**: Dati caricati correttamente
2. **Filtri**: Ricerca, categoria, sotto scorta
3. **Export Excel**: Download funziona
4. **Operazioni CRUD**: Creazione, modifica, eliminazione articoli

---

## Troubleshooting

### CORS Errors

**Sintomo**: Errori "blocked by CORS policy" nella console browser

**Soluzione**:
1. Verifica `CORS_ORIGINS` su Render includa il dominio Vercel
2. Formato: `https://inventario-magazzino.vercel.app,http://localhost:3000`
3. Dopo modifica, redeploy backend su Render

### 404 su API Calls

**Sintomo**: Frontend riceve 404 per chiamate API

**Causa**: `NEXT_PUBLIC_API_URL` non include `/api`

**Soluzione**:
1. Vercel Settings > Environment Variables
2. Modifica `NEXT_PUBLIC_API_URL` a: `https://inventario-magazzino-backend.onrender.com/api`
3. Redeploy frontend

### Database Connection Errors

**Sintomo**: Backend logs mostrano errori connessione database

**Causa Comune**:
- DATABASE_URL non usa pooled endpoint
- Troppe connessioni aperte

**Soluzione**:
1. Verifica DATABASE_URL contenga `.pooler.` nel dominio
2. Esempio corretto: `ep-xxx.pooler.us-east-1.aws.neon.tech`
3. NON usare: `ep-xxx.us-east-1.aws.neon.tech` (direct endpoint)

### Slow First Request (Render)

**Sintomo**: Prima richiesta molto lenta (~50 secondi)

**Causa**: Render free tier spegne l'istanza dopo inattività

**Workaround**:
- Upgrade a Render Piano a Pagamento per istanze always-on
- Implementa keep-alive ping esterno (es. UptimeRobot)

### Build Failures

**Backend**:
- Verifica Dockerfile sintassi corretta
- Check requirements.txt per dipendenze incompatibili
- Logs su Render Dashboard > Logs

**Frontend**:
- Verifica package.json e package-lock.json sincronizzati
- Check TypeScript errors: `npm run type-check`
- Logs su Vercel Dashboard > Deployments > Build Logs

---

## Manutenzione

### Updates

**Backend**:
1. Modifica codice su branch `001-warehouse-inventory-system`
2. Push a GitHub
3. Render auto-deploy (se abilitato) o manual redeploy

**Frontend**:
1. Modifica codice su branch `001-warehouse-inventory-system`
2. Push a GitHub
3. Vercel auto-deploy

### Database Migrations

```bash
# Locale (development)
cd backend
alembic revision --autogenerate -m "descrizione"
alembic upgrade head

# Produzione
# Le migrazioni vengono applicate automaticamente durante deployment backend
```

### Rollback

**Frontend (Vercel)**:
1. Deployments > seleziona deployment precedente
2. Click "Promote to Production"

**Backend (Render)**:
1. Events > trova deployment precedente
2. Click "Rollback"

---

## Best Practices

1. **Environment Variables**: Mai committare credenziali nel repository
2. **Database**: Usa sempre pooled endpoint per Neon
3. **CORS**: Whitelist solo domini necessari
4. **Monitoring**: Configura UptimeRobot per health checks
5. **Backups**: Neon fa backup automatici, verifica configurazione
6. **Logs**: Monitora regolarmente Render e Vercel logs per errori
7. **HTTPS**: Sempre attivo di default su Vercel e Render

---

## Contatti e Supporto

- **Repository**: https://github.com/fracarlesi/inventario_magazzino
- **Branch Produzione**: 001-warehouse-inventory-system
- **Documentation**: README.md, CLAUDE.md

---

**Ultima modifica**: 13 Novembre 2025
**Versione**: 1.0.0
