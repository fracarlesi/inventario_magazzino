# 🤝 Contribuire al Progetto

Grazie per il tuo interesse nel contribuire al Sistema di Gestione Magazzino! Questa guida ti aiuterà a iniziare.

## 📋 Indice

- [Code of Conduct](#code-of-conduct)
- [Come Iniziare](#come-iniziare)
- [Workflow di Sviluppo](#workflow-di-sviluppo)
- [Convenzioni Codice](#convenzioni-codice)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

Questo progetto segue il [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). Partecipando, ti impegni a rispettare questo codice.

## Come Iniziare

### 1. Setup Iniziale

```bash
# Fork il repository su GitHub
# Poi clona il tuo fork
git clone https://github.com/TUO-USERNAME/inventario_magazzino.git
cd inventario_magazzino

# Aggiungi upstream remote
git remote add upstream https://github.com/fracarlesi/inventario_magazzino.git

# Checkout al branch di sviluppo
git checkout 001-warehouse-inventory-system
```

### 2. Setup Ambiente di Sviluppo

Segui la guida completa in [SETUP.md](SETUP.md) per configurare backend e frontend.

### 3. Crea Feature Branch

```bash
# Assicurati di essere aggiornato
git checkout 001-warehouse-inventory-system
git pull upstream 001-warehouse-inventory-system

# Crea nuovo branch per la tua feature
git checkout -b feature/nome-descrittivo

# Oppure per bug fix
git checkout -b fix/nome-bug
```

## Workflow di Sviluppo

### Branch Strategy

- `main` - Codice stabile/production ready
- `001-warehouse-inventory-system` - Branch di sviluppo principale
- `feature/*` - Nuove funzionalità
- `fix/*` - Bug fixes
- `refactor/*` - Refactoring codice
- `docs/*` - Modifiche documentazione

### Commit Messages

Usa messaggi commit chiari in **italiano**:

```bash
# Formato
[Tipo]: Descrizione breve (max 50 caratteri)

Descrizione dettagliata opzionale.
Spiega COSA e PERCHÉ, non COME.

# Esempi
Add: Implementa filtro per categoria nella dashboard
Fix: Corregge validazione giacenza negativa
Update: Migliora performance query inventario
Refactor: Estrae logica validazione in service layer
Docs: Aggiorna guida setup con istruzioni Neon
Test: Aggiunge test per movimento OUT con stock insufficiente
```

**Tipi di commit**:
- `Add:` - Nuove funzionalità
- `Fix:` - Correzione bug
- `Update:` - Miglioramenti a codice esistente
- `Refactor:` - Refactoring senza cambiare comportamento
- `Docs:` - Solo documentazione
- `Test:` - Aggiunta o modifica test
- `Style:` - Formattazione, nessun cambio logica
- `Chore:` - Build, dipendenze, config

## Convenzioni Codice

### Backend (Python)

```bash
# Formattazione
black src/
black tests/

# Linting
flake8 src/
flake8 tests/

# Type checking
mypy src/
```

**Linee guida**:
- Usa **type hints** ovunque
- Docstrings in italiano per funzioni pubbliche
- Messaggi di errore **sempre in italiano**
- Nomi variabili in inglese, commenti in italiano
- Max 100 caratteri per riga

**Esempio**:
```python
async def create_in_movement(
    db: AsyncSession,
    item_id: UUID,
    quantity: Decimal,
    movement_date: date,
    unit_cost_override: Optional[Decimal] = None,
    note: Optional[str] = None,
) -> Movement:
    """
    Crea un movimento di tipo IN (carico merce).

    Args:
        db: Sessione database
        item_id: ID articolo
        quantity: Quantità in ingresso (deve essere > 0)
        movement_date: Data movimento
        unit_cost_override: Costo unitario opzionale per aggiornare articolo
        note: Nota descrittiva opzionale

    Returns:
        Movimento creato

    Raises:
        ValidationError: Se quantity <= 0 o parametri invalidi
        ItemNotFound: Se item_id non esiste
    """
    # Implementation...
```

### Frontend (TypeScript)

```bash
# Formattazione
npm run format
# oppure
prettier --write "src/**/*.{ts,tsx}"

# Linting
npm run lint
```

**Linee guida**:
- Usa **TypeScript strict mode**
- Componenti funzionali con hooks
- Props sempre tipizzate con interface
- Strings UI da `i18n/it.json`, mai hardcoded
- Nomi componenti PascalCase, funzioni camelCase

**Esempio**:
```typescript
interface MovementInFormProps {
  items: ItemWithStock[];
  onSubmit: (data: MovementInCreate) => Promise<void>;
  onCancel: () => void;
  isSubmitting: boolean;
}

export default function MovementInForm({
  items,
  onSubmit,
  onCancel,
  isSubmitting,
}: MovementInFormProps) {
  // Implementation...
}
```

### Localizzazione Italiana

**IMPORTANTE**: Tutta l'interfaccia utente deve essere in italiano!

- ❌ **Mai** hardcodare stringhe in inglese nei component
- ✅ **Sempre** usare `i18n/it.json` per testi UI
- ✅ Messaggi di errore dal backend in italiano
- ✅ Date in formato DD/MM/YYYY
- ✅ Numeri con virgola come separatore decimale (1.234,56)
- ✅ Valute in formato €X.XXX,XX

Prima di fare commit, verifica con la checklist:
[frontend/tests/locale-validation.md](frontend/tests/locale-validation.md)

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Con coverage
pytest --cov=src --cov-report=html

# Solo unit tests
pytest tests/unit

# Solo integration tests
pytest tests/integration

# Test specifico
pytest tests/unit/test_movement_service.py::test_create_in_movement
```

**Linee guida**:
- Test in italiano (nomi funzioni e docstrings)
- Coverage target: >80%
- Test unitari per services/business logic
- Test integrazione per API endpoints

### Frontend Tests

```bash
cd frontend

# Unit tests (Vitest)
npm run test

# Con coverage
npm run test:coverage

# Watch mode
npm run test:watch

# E2E tests (Playwright)
npm run test:e2e

# E2E con UI
npm run test:e2e:ui
```

**Linee guida**:
- Test componenti in italiano
- Coverage target: >70%
- E2E per flussi critici (registrazione movimenti, export Excel)

## Pull Request Process

### 1. Prima di Aprire la PR

Checklist:
- [ ] Codice formattato (Black/Prettier)
- [ ] Linting passa senza errori
- [ ] Test scritti e passano
- [ ] Documentazione aggiornata se necessario
- [ ] Nessun file di config locale committato (.env, .venv, node_modules)
- [ ] Checklist localizzazione verificata per modifiche UI

```bash
# Backend
cd backend
black src/ tests/
flake8 src/ tests/
pytest

# Frontend
cd frontend
npm run format
npm run lint
npm run test
```

### 2. Apri la Pull Request

1. Push del tuo branch:
   ```bash
   git push origin feature/nome-feature
   ```

2. Vai su GitHub e apri PR verso `001-warehouse-inventory-system`

3. **Titolo PR** (in italiano):
   ```
   [Feature] Implementa filtro per data nello storico movimenti
   [Fix] Corregge validazione quantità decimali
   [Refactor] Ottimizza query giacenze
   ```

4. **Descrizione PR** (template):
   ```markdown
   ## Descrizione
   Breve descrizione delle modifiche apportate.

   ## Tipo di Modifica
   - [ ] Bug fix (cambiamento che corregge un problema)
   - [ ] Nuova feature (cambiamento che aggiunge funzionalità)
   - [ ] Breaking change (fix o feature che modifica comportamento esistente)
   - [ ] Documentazione

   ## Motivazione e Contesto
   Perché questa modifica è necessaria? Quale problema risolve?

   ## Come è Stato Testato?
   Descrivi i test eseguiti per verificare le modifiche.

   ## Screenshot (se applicabile)
   Aggiungi screenshot per modifiche UI.

   ## Checklist
   - [ ] Il codice segue le convenzioni del progetto
   - [ ] Ho eseguito self-review del codice
   - [ ] Ho commentato parti complesse
   - [ ] Ho aggiornato la documentazione
   - [ ] Le modifiche non generano nuovi warning
   - [ ] Ho aggiunto test che dimostrano che il fix è efficace o la feature funziona
   - [ ] Test nuovi ed esistenti passano in locale
   - [ ] Verificato checklist localizzazione italiana (se modifiche UI)
   ```

### 3. Code Review

- Rispondi ai commenti di review
- Apporta modifiche richieste
- Push modifiche nello stesso branch (PR si aggiorna automaticamente)
- Una volta approvata, la PR verrà mergiata da un maintainer

## Domande?

- **Issues**: Apri un issue per bug, feature requests o domande
- **Discussions**: Usa GitHub Discussions per domande generali

## Grazie!

Il tuo contributo è molto apprezzato! 🙏

---

**Happy Coding! 🚀**
