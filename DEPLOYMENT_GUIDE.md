# 🚀 Guida Deploy Production - Inventario Magazzino

**Stato attuale**: Database migrato ✅ | Backend ready con Docker ✅ | Deploy da completare ⏳

**Ultima sessione**: 2025-11-12 21:00

---

## 📍 SITUAZIONE ATTUALE

### ✅ Completato:
- Database PostgreSQL su Neon (migrato con successo)
- Migrations eseguite (tabelle create)
- Docker setup per backend (Dockerfile pronto)
- Codice pushato su GitHub branch `001-warehouse-inventory-system`

### ⏳ Da Fare:
1. Deploy backend su Render con Docker
2. Deploy frontend su Vercel
3. Configurare CORS
4. Test finale in produzione

---

## 🔑 CREDENZIALI IMPORTANTI

### Neon Database:
```
Connection String (Pooled):
postgresql://neondb_owner:npg_cEzLjB0sdg1S@ep-raspy-fire-agbe3w45-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require

Database: neondb
User: neondb_owner
Password: npg_cEzLjB0sdg1S
Host: ep-raspy-fire-agbe3w45-pooler.c-2.eu-central-1.aws.neon.tech
```

### GitHub:
```
Repository: https://github.com/fracarlesi/inventario_magazzino
Branch: 001-warehouse-inventory-system
```

---

## 🐳 STEP 1: Deploy Backend su Render (Con Docker)

### Opzione A: Riconfigura servizio esistente

1. Vai su **https://dashboard.render.com**
2. Seleziona il servizio backend esistente
3. **Settings** → Sezione "Build & Deploy"
4. Modifica:
   ```
   Runtime: Docker (cambia da Python 3)
   Root Directory: backend
   Dockerfile Path: ./Dockerfile
   Docker Command: (lascia vuoto)
   ```
5. **Environment Variables** (verifica siano presenti):
   ```
   DATABASE_URL = postgresql://neondb_owner:npg_cEzLjB0sdg1S@ep-raspy-fire-agbe3w45-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require

   CORS_ORIGINS = http://localhost:3000

   DEBUG = false
   ```
6. **Save Changes**
7. **Manual Deploy** → **Clear build cache & deploy**

### Opzione B: Crea nuovo servizio (più pulito)

1. **Cancella servizio vecchio** (se esiste):
   - Settings → Delete Web Service

2. **New +** → **Web Service**

3. **Configurazione**:
   ```
   GitHub Repository: fracarlesi/inventario_magazzino
   Name: inventario-magazzino-backend
   Region: Frankfurt (o Oregon)
   Branch: 001-warehouse-inventory-system
   Root Directory: backend
   Runtime: Docker  ← IMPORTANTE!
   Dockerfile Path: ./Dockerfile
   Instance Type: Free
   ```

4. **Environment Variables** (aggiungi queste 3):

   **Variable 1:**
   ```
   Name: DATABASE_URL
   Value: postgresql://neondb_owner:npg_cEzLjB0sdg1S@ep-raspy-fire-agbe3w45-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require
   ```

   **Variable 2:**
   ```
   Name: CORS_ORIGINS
   Value: http://localhost:3000
   ```

   **Variable 3:**
   ```
   Name: DEBUG
   Value: false
   ```

5. **Create Web Service**

### ⏱️ Tempo Build:
- Docker build: 5-7 minuti
- Dovrebbe completare SENZA errori (Docker risolve i problemi di compilazione Python)

### ✅ Verifica Backend Funzionante:

Quando vedi "Live" (pallino verde):

1. **Copia l'URL** del servizio (es: `https://inventario-magazzino-backend-xyz.onrender.com`)

2. **Testa API**:
   - Vai su: `https://TUO-URL.onrender.com/docs`
   - Dovresti vedere Swagger UI di FastAPI

3. **Salva l'URL** per lo step successivo!

---

## 🎨 STEP 2: Deploy Frontend su Vercel

1. Vai su **https://vercel.com**
2. **Login with GitHub**
3. **Add New...** → **Project**
4. Seleziona: `fracarlesi/inventario_magazzino`

5. **Configurazione**:
   ```
   Framework Preset: Next.js (auto-detect)
   Root Directory: frontend  ← CLICCA "Edit" e scrivi questo!
   Branch: 001-warehouse-inventory-system
   Build Command: npm run build (default)
   Output Directory: .next (default)
   Install Command: npm install (default)
   ```

6. **Environment Variables** (IMPORTANTE - aggiungi queste 3):

   **Variable 1:**
   ```
   Name: NEXT_PUBLIC_API_URL
   Value: https://TUO-BACKEND-URL.onrender.com
   ```
   ⚠️ **Sostituisci con URL Render dello Step 1!**

   **Variable 2:**
   ```
   Name: NEXT_PUBLIC_APP_NAME
   Value: Gestione Magazzino
   ```

   **Variable 3:**
   ```
   Name: NEXT_PUBLIC_DEFAULT_LANGUAGE
   Value: it
   ```

7. **Deploy**

### ⏱️ Tempo Build:
- 2-3 minuti

### ✅ Verifica:
- Ti darà un URL tipo: `https://inventario-magazzino-abc.vercel.app`
- **Salva questo URL!**

---

## 🔗 STEP 3: Aggiorna CORS Backend

Ora che hai l'URL Vercel, devi aggiornare il backend per accettare richieste dal frontend!

1. **Render Dashboard** → Tuo servizio backend
2. **Environment** tab
3. **Trova `CORS_ORIGINS`** e modifica:
   ```
   CORS_ORIGINS = https://TUO-APP.vercel.app,http://localhost:3000
   ```
   ⚠️ **Sostituisci con il tuo URL Vercel reale!**

   Esempio:
   ```
   CORS_ORIGINS = https://inventario-magazzino-abc123.vercel.app,http://localhost:3000
   ```

4. **Save Changes**
5. Render farà redeploy automatico (1-2 min)
6. Aspetta che torni "Live"

---

## 🧪 STEP 4: Test Finale!

### Test 1: Backend API
- Vai su: `https://TUO-BACKEND-URL.onrender.com/docs`
- ✅ Dovresti vedere Swagger UI

### Test 2: Frontend + Database
1. Apri: `https://TUO-APP.vercel.app`
2. ✅ Dovresti vedere la **Dashboard del magazzino**
3. ✅ Nessun errore nella console (F12)

### Test 3: Seed Data (opzionale)
Se non vedi articoli, aggiungi dati di test:

```bash
cd backend
export DATABASE_URL='postgresql://neondb_owner:npg_cEzLjB0sdg1S@ep-raspy-fire-agbe3w45-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require'
./venv/bin/python -m scripts.seed_data
```

### Test 4: Funzionalità Complete
- ✅ Crea un nuovo articolo
- ✅ Fai un movimento IN (carico)
- ✅ Fai un movimento OUT (scarico)
- ✅ Esporta Excel
- ✅ Verifica giacenze aggiornate

---

## 🐛 TROUBLESHOOTING

### Errore: "Network Error" o "Failed to fetch"

**Causa**: CORS non configurato correttamente

**Soluzione**:
1. Verifica che `CORS_ORIGINS` su Render includa l'URL Vercel esatto
2. Nessuno spazio, virgola tra gli URL
3. Includi `https://` nell'URL Vercel

### Errore: "404 Not Found" su Vercel

**Causa**: Root Directory non impostata

**Soluzione**:
1. Vercel Settings → General
2. Root Directory → Edit → Scrivi `frontend`
3. Redeploy

### Errore: Backend "Application failed to respond"

**Causa**: Backend in sleep (Render free tier)

**Soluzione**:
- Aspetta 30-50 secondi (cold start)
- Refresh pagina
- Prima richiesta è sempre lenta su free tier

### Backend: Build fallito

**Causa**: Dockerfile non trovato

**Soluzione**:
1. Verifica Root Directory = `backend`
2. Verifica Dockerfile Path = `./Dockerfile`
3. Verifica Runtime = `Docker` (non Python)

---

## 📊 ARCHITETTURA FINALE

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       ↓
┌─────────────────────┐
│  Vercel (Frontend)  │  https://inventario-magazzino.vercel.app
│    Next.js + React  │
└──────┬──────────────┘
       │ API calls
       ↓
┌─────────────────────┐
│  Render (Backend)   │  https://inventario-magazzino-backend.onrender.com
│  FastAPI + Docker   │
└──────┬──────────────┘
       │ SQL queries
       ↓
┌─────────────────────┐
│  Neon (Database)    │  PostgreSQL 15
│     Pooled          │
└─────────────────────┘
```

---

## 📝 CHECKLIST FINALE

Quando tutto funziona:

- [ ] Backend Render "Live" e risponde su /docs
- [ ] Frontend Vercel accessibile
- [ ] Dashboard mostra statistiche
- [ ] Possibile creare articoli
- [ ] Possibile fare movimenti IN/OUT
- [ ] Export Excel funziona
- [ ] Nessun errore console browser

---

## 🔄 PROSSIME SESSIONI

### Setup Playwright MCP (per automazione future)

Se vuoi automatizzare deploy e configurazioni in futuro:

```bash
# Installare Playwright MCP
npm install -g @executeautomation/mcp-playwright

# Configurare in Claude Code
# File: ~/.claude/mcp_settings.json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@executeautomation/mcp-playwright"]
    }
  }
}
```

Poi riavvia Claude Code e avrai automazione browser!

---

## 📧 CONTATTI & LINK UTILI

- **GitHub Repo**: https://github.com/fracarlesi/inventario_magazzino
- **Neon Dashboard**: https://console.neon.tech
- **Render Dashboard**: https://dashboard.render.com
- **Vercel Dashboard**: https://vercel.com/dashboard

---

## 🎯 STATO CORRENTE

**Completamento Deploy**: ~70%

**Mancano**:
1. Deploy backend Render con Docker (10 min)
2. Deploy frontend Vercel (5 min)
3. Configurare CORS (2 min)
4. Test (3 min)

**Totale tempo stimato**: ~20 minuti

---

**Buona fortuna! 🚀**

**Quando riprendi la sessione con Playwright MCP installato, potrai automatizzare tutto questo!**
