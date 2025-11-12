# Feature Specification: Sistema di Gestione Magazzino Officina

**Feature Branch**: `001-warehouse-inventory-system`
**Created**: 2025-11-11
**Status**: Draft
**Input**: User description: "Costruisci una piccola web-app di gestione magazzino per una singola officina con registrazione entrate/uscite articoli, inventario aggiornato ed export Excel ultimi 12 mesi"

## Clarifications

### Session 2025-11-11

- Q: Come deve gestire il sistema le modifiche concorrenti allo stock dello stesso articolo quando l'utente ha più schede/sessioni browser aperte? → A: Last-write-wins (nessun rilevamento conflitti, implementazione più semplice)
- Q: Il sistema deve aggiornare automaticamente la tabella inventario della dashboard quando vengono registrati movimenti, o richiedere refresh manuale? → A: Auto-refresh immediato dopo ogni movimento (IN/OUT/ADJUSTMENT) usando SWR mutate
- Q: Qual è il tempo massimo di risposta accettabile per l'endpoint di export Excel quando genera file con volumi limite (10.000 movimenti)? → A: Sotto 30 secondi (più realistico per 10K+ movimenti su free tier con cold starts)
- Q: Che livello di logging/monitoring errori è richiesto per le operazioni in produzione, considerando i vincoli free tier e lo scope single-user? → A: Minimale - Solo log Render built-in, nessun monitoring esterno (zero costi)
- Q: Il sistema deve prevenire o permettere l'eliminazione di categorie che sono attualmente assegnate a articoli esistenti? → A: Categorie sono testo libero, non entità - eliminazione non applicabile (confermata assumption esistente)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualizzare e Cercare Inventario Corrente (Priority: P1)

L'utente dell'officina apre l'applicazione e vede immediatamente l'elenco completo degli articoli in magazzino con le giacenze aggiornate. Può cercare articoli per nome, filtrare per categoria, e identificare rapidamente gli articoli sotto scorta minima.

**Why this priority**: Questa è la funzionalità fondamentale - senza poter vedere cosa c'è in magazzino, l'applicazione non ha valore. È l'MVP assoluto.

**Independent Test**: Può essere testato completamente aprendo l'applicazione e verificando che mostri correttamente l'elenco degli articoli con giacenze, filtri e indicatori di sotto-scorta. Fornisce valore immediato anche senza altre funzionalità.

**Acceptance Scenarios**:

1. **Given** il magazzino ha 20 articoli con giacenze diverse, **When** l'utente apre la dashboard principale, **Then** vede una tabella con tutti gli articoli che mostra: nome, categoria, unità di misura, giacenza attuale, scorta minima, costo unitario e stato (OK/Sotto scorta)
2. **Given** l'utente è nella dashboard, **When** digita "bullone" nella barra di ricerca, **Then** la tabella mostra solo gli articoli il cui nome contiene "bullone"
3. **Given** il magazzino ha articoli in 5 categorie diverse, **When** l'utente seleziona la categoria "Filtri olio", **Then** la tabella mostra solo gli articoli di quella categoria
4. **Given** ci sono 3 articoli con giacenza inferiore alla scorta minima, **When** l'utente attiva il toggle "solo sotto scorta", **Then** vede solo questi 3 articoli evidenziati
5. **Given** un articolo ha giacenza 5 e scorta minima 10, **When** l'utente visualizza l'inventario, **Then** l'articolo è marcato come "Sotto scorta" con indicazione visiva chiara

---

### User Story 2 - Registrare Carico Merce (IN) (Priority: P2)

L'utente riceve nuova merce e deve registrare l'entrata nel magazzino. Seleziona l'articolo, indica la quantità ricevuta, la data (default oggi) e opzionalmente un nuovo costo unitario e note. Il sistema aggiorna automaticamente la giacenza.

**Why this priority**: Senza poter registrare gli ingressi, l'inventario diventa obsoleto. È la seconda funzionalità critica dopo la visualizzazione.

**Independent Test**: Può essere testato creando un movimento IN per un articolo esistente e verificando che la giacenza si aggiorni correttamente. Funziona anche se User Story 3 (scarico) non è implementata.

**Acceptance Scenarios**:

1. **Given** l'articolo "Olio motore 5W30" ha giacenza 10, **When** l'utente registra un carico di 20 unità, **Then** la giacenza diventa 30
2. **Given** l'utente sta registrando un carico, **When** seleziona l'articolo tramite ricerca nome, inserisce quantità 15, lascia data default (oggi) e aggiunge nota "Fornitore A", **Then** il sistema salva il movimento con tutti i dettagli e timestamp corrente
3. **Given** un articolo ha costo unitario €5.00, **When** l'utente registra un carico con costo unitario override di €5.50, **Then** il costo unitario dell'articolo viene aggiornato a €5.50
4. **Given** l'utente sta per registrare un carico, **When** inserisce quantità 0 o negativa, **Then** il sistema blocca l'operazione con messaggio "La quantità deve essere maggiore di zero"
5. **Given** un articolo "Filtro aria" era sotto scorta (giacenza 3, minimo 5), **When** l'utente carica 10 unità portando la giacenza a 13, **Then** l'articolo non è più marcato come "Sotto scorta"

---

### User Story 3 - Registrare Scarico Merce (OUT) (Priority: P3)

L'utente utilizza materiale per una riparazione e deve registrare l'uscita. Seleziona l'articolo, indica la quantità usata. Il sistema verifica che ci sia giacenza sufficiente prima di confermare, mostrando un avviso se l'operazione porterebbe sotto zero.

**Why this priority**: Completa il ciclo di gestione magazzino. Meno critico del carico perché molte officine partono con inventario esistente e le prime operazioni sono spesso carichi.

**Independent Test**: Può essere testato creando un movimento OUT per un articolo con giacenza sufficiente e verificando che: (a) con giacenza adeguata, lo scarico procede e la giacenza si riduce; (b) con giacenza insufficiente, il sistema blocca con messaggio chiaro. Funziona indipendentemente dalle altre user stories.

**Acceptance Scenarios**:

1. **Given** l'articolo "Pastiglie freno" ha giacenza 8, **When** l'utente registra uno scarico di 2 unità, **Then** la giacenza diventa 6
2. **Given** l'utente sta per scaricare 5 unità di un articolo con giacenza 3, **When** tenta di confermare l'operazione, **Then** il sistema blocca e mostra "Impossibile scaricare 5 unità. Giacenza disponibile: 3"
3. **Given** l'utente ha inserito articolo e quantità valida, **When** sta per confermare lo scarico, **Then** vede un messaggio di conferma "Stai per scaricare X unità di [Nome articolo], giacenza disponibile Y"
4. **Given** l'utente registra uno scarico, **When** inserisce data, quantità e nota "Usato per riparazione Alfa Romeo 159", **Then** il movimento viene salvato con tutti i dettagli
5. **Given** un articolo ha giacenza 10 e scorta minima 8, **When** l'utente scarica 5 unità portando la giacenza a 5, **Then** l'articolo viene marcato "Sotto scorta"

---

### User Story 4 - Gestire Anagrafica Articoli (Priority: P4)

L'utente può creare nuovi articoli in magazzino, modificare le informazioni esistenti (nome, categoria, unità, note, scorta minima, costo), ed eliminare articoli non più utilizzati (solo se giacenza zero e nessun movimento negli ultimi 12 mesi).

**Why this priority**: Necessario per manutenzione a lungo termine, ma non critico per l'uso quotidiano iniziale. L'officina parte spesso con anagrafica esistente.

**Independent Test**: Può essere testato creando un nuovo articolo, modificandone le proprietà, e tentando di eliminarlo (con e senza vincoli). Funziona indipendentemente dai movimenti.

**Acceptance Scenarios**:

1. **Given** l'utente vuole aggiungere un nuovo articolo, **When** inserisce nome "Filtro abitacolo", categoria "Filtri", unità "pz", note "Formato universale", scorta minima 5, costo €8.50, **Then** il sistema crea l'articolo con giacenza iniziale 0
2. **Given** un articolo esistente ha categoria "Filtri", **When** l'utente inizia a digitare nel campo categoria, **Then** vede suggerimenti autocomplete con categorie già usate
3. **Given** un articolo ha giacenza 0 e nessun movimento negli ultimi 13 mesi, **When** l'utente clicca "Elimina", **Then** il sistema elimina l'articolo dopo conferma
4. **Given** un articolo ha giacenza 5, **When** l'utente tenta di eliminarlo, **Then** il sistema blocca con messaggio "Impossibile eliminare: giacenza non zero"
5. **Given** un articolo ha giacenza 0 ma ha movimenti negli ultimi 6 mesi, **When** l'utente tenta di eliminarlo, **Then** il sistema blocca con messaggio "Impossibile eliminare: l'articolo ha movimenti recenti (ultimi 12 mesi)"
6. **Given** l'utente modifica un articolo, **When** cambia il costo unitario da €5 a €6, **Then** il nuovo costo viene salvato e usato per calcoli futuri (senza modificare movimenti storici)

---

### User Story 5 - Consultare Storico Movimenti (Priority: P5)

L'utente vuole vedere lo storico completo dei movimenti di magazzino per verificare quando è entrato o uscito un articolo, con possibilità di filtrare per data, articolo specifico, o tipo di movimento (IN/OUT).

**Why this priority**: Utile per audit e verifiche, ma non necessario per operazioni quotidiane. Il valore principale è nell'inventario corrente.

**Independent Test**: Può essere testato visualizzando la lista movimenti con vari filtri (ultimi 30 giorni, articolo specifico, solo IN o solo OUT) e verificando che mostri i dati corretti. Funziona anche se export Excel non è implementato.

**Acceptance Scenarios**:

1. **Given** ci sono 50 movimenti negli ultimi 3 mesi, **When** l'utente apre la pagina Movimenti, **Then** vede i movimenti degli ultimi 30 giorni in ordine cronologico inverso (più recenti prima)
2. **Given** l'utente è nella pagina Movimenti, **When** filtra per articolo "Olio motore 5W30", **Then** vede solo i movimenti relativi a quell'articolo
3. **Given** l'utente sta visualizzando i movimenti, **When** filtra per tipo "OUT", **Then** vede solo gli scarichi
4. **Given** l'utente imposta filtro data dal 01/01/2025 al 31/03/2025, **When** applica il filtro, **Then** vede solo movimenti in quel range
5. **Given** un movimento IN ha unit_cost_override €12.50 e nota "Fornitore B - fattura 123", **When** l'utente visualizza lo storico, **Then** vede tutte queste informazioni nella tabella

---

### User Story 6 - Esportare Dati in Excel (Priority: P6)

L'utente vuole esportare l'intero inventario corrente e lo storico movimenti degli ultimi 12 mesi in un file Excel (.xlsx) per archiviazione, analisi esterna, o invio al commercialista.

**Why this priority**: Importante per compliance e backup, ma non necessario per l'uso quotidiano. Può essere aggiunto per ultimo.

**Independent Test**: Può essere testato cliccando il pulsante "Esporta Excel" e verificando che il file scaricato: (a) sia formato .xlsx, (b) contenga due fogli (Inventario e Movimenti_ultimi_12_mesi), (c) mostri tutti i dati corretti con formattazione adeguata. Funziona indipendentemente da tutte le altre funzionalità.

**Acceptance Scenarios**:

1. **Given** l'utente è nella dashboard principale, **When** clicca "Esporta Excel (ultimi 12 mesi)", **Then** il browser scarica un file "magazzino_YYYYMMDD.xlsx"
2. **Given** l'utente apre il file Excel esportato, **When** visualizza il foglio "Inventario", **Then** vede colonne: Nome, Categoria, Unità, Giacenza, Min. Scorta, Sotto Scorta (Sì/No), Costo Unitario, Valore (Giacenza×Costo), Note - con header in grassetto e numeri formattati a 2 decimali
3. **Given** l'utente apre il file Excel esportato, **When** visualizza il foglio "Movimenti_ultimi_12_mesi", **Then** vede colonne: Data, Articolo, Tipo (IN/OUT/ADJUSTMENT), Quantità, Unità, Costo Unitario usato, Nota - con dati ordinati per data
4. **Given** oggi è 15/11/2025 e ci sono movimenti da gennaio 2024 a novembre 2025, **When** l'utente esporta, **Then** il foglio Movimenti contiene solo i movimenti dal 15/11/2024 in poi
5. **Given** il file Excel è stato generato, **When** l'utente apre le colonne, **Then** le colonne hanno larghezza automatica adeguata al contenuto

---

### User Story 7 - Rettificare Inventario per Riconciliazione Fisica (Priority: P4)

L'utente effettua un conteggio fisico periodico del magazzino e scopre discrepanze tra la giacenza reale e quella calcolata dal sistema. Deve poter registrare una rettifica per allineare i dati, documentando il motivo della correzione.

**Why this priority**: Essenziale per mantenere l'accuratezza a lungo termine e seguire le best practices di warehouse management. Va inserita prima dell'export Excel ma dopo le operazioni base. Non critica per l'MVP iniziale ma importante per operazioni continuative.

**Independent Test**: Può essere testato creando un movimento ADJUSTMENT per un articolo, specificando la nuova giacenza target e una nota obbligatoria. Il sistema deve calcolare automaticamente la quantità di rettifica (+/-) e aggiornare la giacenza. Funziona indipendentemente dalle altre user stories.

**Acceptance Scenarios**:

1. **Given** l'articolo "Filtro olio" ha giacenza calcolata 15 ma il conteggio fisico mostra 13, **When** l'utente registra rettifica con giacenza target 13 e nota "Conteggio fisico mensile - 2 unità danneggiate", **Then** il sistema crea movimento ADJUSTMENT con quantità -2 e la giacenza diventa 13
2. **Given** l'utente sta registrando una rettifica, **When** inserisce giacenza target uguale alla giacenza corrente, **Then** il sistema blocca con messaggio "La giacenza target coincide con quella attuale. Nessuna rettifica necessaria."
3. **Given** un articolo ha giacenza 10, **When** l'utente registra rettifica con target 15 e nota "Trovate 5 unità in magazzino secondario", **Then** il sistema crea ADJUSTMENT +5 e la giacenza diventa 15
4. **Given** l'utente sta registrando una rettifica, **When** tenta di confermare senza inserire una nota, **Then** il sistema blocca con messaggio "La nota è obbligatoria per le rettifiche (spiega il motivo della discrepanza)"
5. **Given** l'utente visualizza lo storico movimenti, **When** filtra per tipo "ADJUSTMENT", **Then** vede solo le rettifiche con evidenza chiara del delta (+/-) e nota esplicativa
6. **Given** una rettifica porta la giacenza da 20 a 5 (sotto scorta minima 8), **When** il movimento viene salvato, **Then** l'articolo viene marcato "Sotto scorta" come per normali movimenti OUT

---

### Edge Cases

- **Giacenza zero persistente**: Cosa succede se un articolo rimane a giacenza zero per mesi? Il sistema deve permettere comunque carichi futuri senza eliminare l'articolo.
- **Movimenti simultanei**: Se l'utente ha più schede aperte e registra movimenti contemporaneamente, il sistema deve gestire la concorrenza evitando giacenze inconsistenti.
- **Quantità con decimali**: Per articoli venduti a peso o litri (es. olio sfuso), il sistema deve supportare quantità decimali (es. 2.5 litri), non solo numeri interi.
- **Articoli senza categoria**: Alcuni articoli potrebbero non avere categoria assegnata - il sistema deve gestirli correttamente nei filtri (es. opzione "Senza categoria").
- **Storico molto lungo**: Se ci sono migliaia di movimenti, il filtro data predefinito (ultimi 30 giorni) evita di caricare troppi dati. L'export Excel deve gestire grandi volumi (migliaia di righe).
- **Eliminazione con storico**: Un articolo eliminabile (giacenza 0, nessun movimento recente) potrebbe avere movimenti vecchi (>12 mesi) - questi vanno preservati o eliminati? Assumiamo preservazione per audit.
- **Costo zero**: Un articolo può avere costo unitario zero (materiali recuperati, omaggi) - deve essere permesso.
- **Note lunghe**: Le note potrebbero contenere testo molto lungo - il sistema deve gestire troncamento/espansione nell'interfaccia.
- **Data futura nei movimenti**: L'utente potrebbe erroneamente inserire data futura - il sistema deve validare o permettere (se ci sono casi d'uso di pre-registrazione)?
- **Rettifiche multiple stesso articolo**: Se l'utente registra più rettifiche sullo stesso articolo in breve tempo, il sistema deve permetterlo (ogni ADJUSTMENT è indipendente e si somma algebricamente).
- **Rettifica a giacenza negativa**: È possibile rettificare portando la giacenza sotto zero? Il sistema deve bloccare (coerente con vincolo OUT) o permettere documentando furto/perdita totale?
- **Valore magazzino con articoli senza costo**: Il calcolo del valore totale magazzino deve ignorare articoli con costo 0 o includerli? Assumiamo inclusione con contributo 0.
- **Notifiche quando nessun articolo sotto scorta**: Il sistema deve inviare notifica giornaliera anche se tutti gli articoli sono OK, o solo quando ci sono alert? Assumiamo invio solo se ci sono articoli sotto scorta.
- **Banner sotto scorta permanente**: Se un articolo rimane sotto scorta per settimane, il banner deve rimanere visibile o l'utente può dismissarlo temporaneamente? Assumiamo banner persistente non dismissibile (critical alert).

### Edge Case Decision Matrix

Decisioni prese per i casi ambigui identificati sopra:

| Edge Case | Decision | Rationale | Implementation Reference |
|-----------|----------|-----------|--------------------------|
| **Data futura nei movimenti** | BLOCK if movement_date > TODAY | Previene errori di input accidentali | FR-019 extended: validate_date_range in validation.py (T083.1) |
| **Data troppo passata** | BLOCK if movement_date < (TODAY - 365 days) | Limita registrazioni posticipate eccessive | FR-019 extended: validate_date_range max_past_days=365 |
| **Rettifica a giacenza negativa** | BLOCK (target_stock >= 0 required) | Consistenza con vincolo OUT, no negative inventory | FR-037 extended: ADJUSTMENT validation in T061 |
| **Articoli senza categoria** | ALLOW NULL, show "Senza categoria" in filter | Flessibilità operativa, categoria opzionale | FR-003 extended: CategoryFilter component (T026) includes NULL option |
| **Valore magazzino con costo 0** | INCLUDE with zero contribution | Calcolo accurato valore totale reale | FR-041 extended: SUM includes all items, cost=0 valid (T021) |
| **Notifiche email quando tutto OK** | NO SEND (only when under-stock count > 0) | Riduce noise, focus su alert critici | FR-044 extended: conditional send logic |
| **Banner sotto scorta dismissibile** | NOT DISMISSIBLE (persistent critical alert) | Garantisce visibilità articoli critici | FR-045: DashboardStats banner always visible if count > 0 (T028) |
| **Eliminazione preserva storico** | YES (keep movements >12 months) | Audit trail completo anche per articoli obsoleti | FR-015: delete only blocks if recent movements, old preserved |
| **Giacenza zero persistente** | ALLOW indefinitely | Articolo dormant può ricevere carichi futuri | No blocking logic, giacenza=0 is valid state |
| **Rettifiche multiple stesso articolo** | ALLOW (each ADJUSTMENT independent) | Ogni correzione è evento separato sommabile | FR-036: No uniqueness constraint on ADJUSTMENT movements |
| **Quantità decimali** | SUPPORT up to 3 decimal places | Articoli a peso/volume (2.500 kg olio) | FR-021: validate_decimal(decimal_places=3) in T083.1 |
| **Costo zero** | ALLOW (unit_cost = 0 valid) | Omaggi, materiali recuperati | FR-013: min constraint unit_cost >= 0, zero allowed |

**Decision Authority**: Based on spec assumptions (lines 269-277), tasks.md implementation (Phase 2-10), and constitution principle II (Data Integrity) requiring consistency.

## Requirements *(mandatory)*

### Functional Requirements

**Gestione Inventario**

- **FR-001**: Il sistema MUST mostrare in tempo reale la giacenza corrente di ogni articolo, calcolata come somma algebrica di tutti i movimenti (IN positivi, OUT negativi)
- **FR-002**: Il sistema MUST permettere ricerca articoli per nome (matching parziale, case-insensitive)
- **FR-003**: Il sistema MUST permettere filtro articoli per categoria
- **FR-004**: Il sistema MUST permettere visualizzazione "solo sotto scorta" che mostra articoli con giacenza < scorta minima
- **FR-005**: Il sistema MUST evidenziare visivamente gli articoli sotto scorta minima

**Gestione Movimenti**

- **FR-006**: Il sistema MUST permettere registrazione movimenti di tipo IN (carico) con: articolo, quantità (>0), data (default oggi), nota opzionale, costo unitario override opzionale
- **FR-007**: Il sistema MUST permettere registrazione movimenti di tipo OUT (scarico) con: articolo, quantità (>0), data (default oggi), nota opzionale
- **FR-008**: Il sistema MUST validare che movimenti OUT non portino giacenza sotto zero, bloccando l'operazione e mostrando messaggio chiaro con giacenza disponibile
- **FR-009**: Il sistema MUST richiedere conferma esplicita prima di registrare un movimento OUT, mostrando quantità da scaricare e giacenza disponibile
- **FR-010**: Il sistema MUST aggiornare il costo unitario dell'articolo quando un movimento IN ha unit_cost_override valorizzato
- **FR-011**: Il sistema MUST salvare timestamp server-side per ogni movimento (non timestamp client)
- **FR-012**: Il sistema MUST garantire atomicità dei movimenti (transazioni database)
- **FR-036**: Il sistema MUST permettere registrazione movimenti di tipo ADJUSTMENT (rettifica) con: articolo, giacenza target, nota obbligatoria
- **FR-037**: Il sistema MUST calcolare automaticamente la quantità di rettifica come differenza tra giacenza target e giacenza corrente (positiva o negativa)
- **FR-038**: Il sistema MUST bloccare rettifiche con giacenza target uguale a giacenza corrente con messaggio "Nessuna rettifica necessaria"
- **FR-039**: Il sistema MUST rendere obbligatoria la nota per movimenti ADJUSTMENT, bloccando se vuota
- **FR-040**: Il sistema MUST mostrare movimenti ADJUSTMENT nello storico con evidenza visiva del delta calcolato (+/-)

**Gestione Articoli**

- **FR-013**: Il sistema MUST permettere creazione nuovi articoli con: nome (required), categoria (optional), unità di misura (default "pz"), note (optional), scorta minima (default 0), costo unitario (default 0)
- **FR-014**: Il sistema MUST permettere modifica articoli esistenti per tutti i campi eccetto giacenza (che si modifica solo via movimenti)
- **FR-015**: Il sistema MUST permettere eliminazione articoli solo se: giacenza = 0 AND nessun movimento negli ultimi 12 mesi
- **FR-016**: Il sistema MUST bloccare eliminazione articoli con giacenza > 0 con messaggio chiaro
- **FR-017**: Il sistema MUST bloccare eliminazione articoli con movimenti recenti (<12 mesi) con messaggio chiaro
- **FR-018**: Il sistema MUST fornire autocomplete per categorie e unità basato su valori già esistenti nel database

**Validazioni**

- **FR-019**: Il sistema MUST validare che quantità movimenti sia > 0
- **FR-020**: Il sistema MUST validare che nome articolo sia non vuoto
- **FR-021**: Il sistema MUST validare formato numerico per quantità, scorta minima, costi

**Storico e Audit**

- **FR-022**: Il sistema MUST permettere visualizzazione storico movimenti con filtri: range date (default ultimi 30 giorni), articolo specifico, tipo movimento (IN/OUT/ADJUSTMENT/Tutti)
- **FR-023**: Il sistema MUST mostrare per ogni movimento: data/ora, articolo, tipo, quantità, unità, costo unitario (se applicabile), nota
- **FR-024**: Il sistema MUST ordinare movimenti per data decrescente (più recenti prima)

**Export Excel**

- **FR-025**: Il sistema MUST generare file Excel (.xlsx, non CSV) con nome "magazzino_YYYYMMDD.xlsx"
- **FR-026**: Il sistema MUST includere foglio "Inventario" con colonne: Nome, Categoria, Unità, Giacenza, Min. Scorta, Sotto Scorta (Sì/No), Costo Unitario, Valore (Giacenza×Costo), Note
- **FR-027**: Il sistema MUST includere foglio "Movimenti_ultimi_12_mesi" con colonne: Data, Articolo, Tipo (IN/OUT/ADJUSTMENT), Quantità, Unità, Costo Unitario usato, Nota
- **FR-028**: Il sistema MUST filtrare movimenti export per ultimi 12 mesi dalla data corrente
- **FR-029**: Il sistema MUST formattare Excel con: header grassetto, auto-width colonne, numeri con 2 decimali dove appropriato

**Interfaccia Utente**

- **FR-030**: Il sistema MUST mostrare pulsanti grandi e chiari con etichette "Carico (IN)", "Scarico (OUT)" e "Rettifica"
- **FR-031**: Il sistema MUST fornire placeholder esplicativi nei form (es. "es: bulloni M8")
- **FR-032**: Il sistema MUST mostrare messaggi di validazione e errore in italiano, chiari e semplici
- **FR-033**: Il sistema MUST richiedere conferma per operazioni distruttive (OUT che riduce giacenza, Elimina articolo, ADJUSTMENT)
- **FR-034**: Il sistema MUST supportare navigazione tastiera (Tab) e focus visibile per accessibilità base
- **FR-041**: Il sistema MUST mostrare nella dashboard il valore totale magazzino calcolato come somma(giacenza × costo unitario) per tutti gli articoli
- **FR-042**: Il sistema MUST mostrare il conteggio articoli sotto scorta nella dashboard (es. "5 articoli sotto scorta")
- **FR-046**: Il sistema MUST aggiornare automaticamente la tabella inventario dashboard dopo ogni movimento registrato (IN/OUT/ADJUSTMENT) usando invalidazione cache client-side (SWR mutate) per garantire giacenze visibili entro <1 secondo (vedi SC-002)

**Notifiche e Alerting**

- **FR-043**: Il sistema SHOULD permettere attivazione notifiche giornaliere via interfaccia (opzionale, disattivabile dall'utente)
- **FR-044**: Il sistema SHOULD inviare riepilogo giornaliero con lista articoli sotto scorta quando la funzionalità è attivata
- **FR-045**: Il sistema MUST mostrare banner in-app persistente quando ci sono articoli sotto scorta, con link diretto alla vista filtrata

**Localizzazione**

- **FR-035**: Tutta l'interfaccia utente MUST essere in italiano (etichette, messaggi, date)

### Key Entities

- **Articolo (Item)**: Rappresenta un prodotto/componente in magazzino. Attributi: identificativo univoco, nome, categoria, unità di misura, note descrittive, soglia scorta minima, costo unitario corrente, data creazione. La giacenza NON è attributo diretto ma calcolata dai movimenti.

- **Movimento (Movement)**: Rappresenta un'operazione di carico (IN), scarico (OUT) o rettifica (ADJUSTMENT) su un articolo. Attributi: identificativo univoco, riferimento all'articolo, tipo operazione (IN/OUT/ADJUSTMENT), quantità (può essere negativa per ADJUSTMENT), timestamp operazione, nota testuale (obbligatoria per ADJUSTMENT, opzionale per IN/OUT), costo unitario override (solo per IN). Ogni movimento è immutabile dopo creazione.

- **Giacenza Corrente (Computed Stock)**: Non è entità fisica ma vista/calcolo: per ogni articolo, somma(quantità) di movimenti dove IN è positivo, OUT è negativo, e ADJUSTMENT può essere positivo o negativo.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: L'utente può registrare un movimento di magazzino (IN, OUT o ADJUSTMENT) in meno di 30 secondi dal momento in cui apre l'applicazione
- **SC-002**: La giacenza visualizzata nella dashboard si aggiorna immediatamente (<1 secondo) dopo ogni movimento registrato (IN/OUT/ADJUSTMENT)
- **SC-003**: Il sistema previene correttamente il 100% dei tentativi di scarico che porterebbero giacenza negativa, mostrando messaggio di errore chiaro
- **SC-004**: L'export Excel degli ultimi 12 mesi viene generato e scaricato in meno di 10 secondi con 5000 movimenti, meno di 30 secondi con 10000 movimenti (edge-case volume su free tier con cold starts)
- **SC-005**: L'utente può identificare visivamente gli articoli sotto scorta in meno di 5 secondi guardando la dashboard (evidenziazione + conteggio + banner)
- **SC-006**: Il 90% degli utenti riesce a completare le operazioni principali (carico, scarico, rettifica, ricerca articolo) al primo tentativo senza bisogno di aiuto o documentazione
- **SC-007**: Il sistema mantiene consistenza dati al 100%: nessuna giacenza negativa non documentata, nessun movimento con quantità ≤0 (eccetto ADJUSTMENT), nessuna transazione parziale
- **SC-008**: Il file Excel esportato è apribile direttamente in Excel/LibreOffice senza errori di formato e con formattazione corretta (header grassetto, colonne auto-width, numeri 2 decimali)
- **SC-009**: Il sistema supporta almeno 1000 articoli e 10000 movimenti senza degradazione prestazionale percepibile (caricamento pagine <2 secondi)
- **SC-010**: L'interfaccia è completamente navigabile via tastiera (Tab, Enter, Esc) per accessibilità base
- **SC-011**: Il valore totale magazzino visualizzato nella dashboard è accurato al 100% e si aggiorna in tempo reale dopo ogni movimento o modifica costo
- **SC-012**: Il banner sotto scorta è visibile immediatamente quando almeno un articolo scende sotto soglia minima e scompare quando tutti tornano sopra soglia
- **SC-013**: Il 100% delle rettifiche (ADJUSTMENT) ha nota esplicativa documentando il motivo della discrepanza (validazione obbligatoria)

## Assumptions

- **Single-user environment**: Non è richiesta autenticazione o gestione multi-utente. L'applicazione è dedicata a una singola officina con accesso diretto.
- **Browser moderno**: L'utente utilizza browser aggiornato (Chrome, Firefox, Safari, Edge ultimi 2 anni) con JavaScript abilitato.
- **Unità di misura libere**: Le unità (pz, kg, lt, m, ecc.) sono testo libero con autocomplete, non enumerate rigidamente.
- **Categorie libere**: Le categorie sono testo libero con autocomplete, permettendo flessibilità per esigenze specifiche officina.
- **Giacenza calcolata runtime**: Non si mantiene campo giacenza denormalizzato nelle tabelle, ma si calcola on-the-fly aggregando movimenti. Se prestazioni diventano problema, si può materializzare con trigger/view.
- **Concurrency strategy (multi-tab)**: Il sistema usa strategia last-write-wins per modifiche concorrenti. Se l'utente ha più tab aperte e registra movimenti simultaneamente, prevale l'ultima scrittura senza rilevamento conflitti. Semplicità di implementazione prioritaria su conflict detection per scenario single-user. Race conditions su stock sono accettabili data la bassa frequenza attesa di operazioni simultanee.
- **Eliminazione preserva storico**: Anche se un articolo è eliminabile (vincoli rispettati), i suoi movimenti storici >12 mesi rimangono nel database per audit trail completo.
- **Timezone server-side**: Tutti i timestamp sono gestiti server-side per evitare inconsistenze da timezone client diversi.
- **Nessun barcode**: Non è richiesta integrazione con lettori barcode o QR. Input manuale via tastiera/mouse.
- **Nessun grafico/analytics**: Non sono richieste dashboard grafiche, KPI, o analytics avanzate. Solo tabelle dati.
- **Free tier compatibile**: Tutti i servizi devono essere gratuiti (Vercel, Supabase/Neon free tier) quindi limiti volume dati realistici (~10MB DB, ~100k req/mese).
- **Observability minimale**: Produzione usa solo log Render built-in (7 giorni retention) per debugging. Nessun monitoring esterno (Sentry, Datadog) o alerting automatico necessario per scenario single-user. Health check endpoint (/health) consente verifica uptime manuale. UptimeRobot ping opzionale può essere aggiunto post-deploy se richiesto.
- **Data validation**: Le date nei movimenti possono essere nel passato (registrazione posticipata) ma non oltre 365 giorni nel passato né nel futuro (prevenire errori).
- **Quantità decimali**: Supporto per quantità con fino a 3 decimali (es. 2.500 kg) per articoli venduti a peso/volume.
- **Costo può essere zero**: Articoli con costo unitario 0 sono permessi (omaggi, recupero materiali).
- **Export è client-side**: La generazione .xlsx avviene nel browser con libreria SheetJS per ridurre carico server e sfruttare free tier.
- **Rettifiche ADJUSTMENT**: Le rettifiche inventario sono trattate come movimenti immutabili con quantità positiva o negativa calcolata automaticamente dal sistema. La nota obbligatoria fornisce audit trail per discrepanze.
- **Banner sotto scorta persistente**: Il banner di alert non è dismissibile dall'utente per garantire che gli articoli critici sotto scorta non vengano ignorati.
- **Notifiche email opzionali**: Le notifiche giornaliere via email sono funzionalità SHOULD (opzionale) e possono essere implementate post-MVP se richiesto dall'utente.
- **Valore magazzino include costo zero**: Il calcolo del valore totale magazzino include tutti gli articoli, anche quelli con costo unitario 0 (contributo nullo al totale).
- **Rettifiche non possono portare giacenza negativa**: Coerentemente con il vincolo OUT, le rettifiche ADJUSTMENT devono rispettare giacenza ≥ 0 (a meno che non sia esplicitamente documentata perdita totale).
