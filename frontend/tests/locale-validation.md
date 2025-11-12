# Italian Locale Validation Checklist (T083.2)

**Purpose**: Verify all UI strings, formats, and messages are in Italian per FR-035
**Created**: 2025-11-12
**Status**: Pre-deployment validation required

## UI Strings Validation

- [ ] No hardcoded English strings in components (check all .tsx files)
- [ ] All labels use `it.json` translations
- [ ] All buttons use Italian text (Carico, Scarico, Rettifica, Elimina, Salva, Annulla)
- [ ] All placeholders use Italian (e.g., "es: bulloni M8", "Cerca per nome...")
- [ ] All validation error messages in Italian
- [ ] All API error messages returned in Italian from backend
- [ ] All modal/dialog titles in Italian
- [ ] All form field labels in Italian
- [ ] Table column headers in Italian (Nome, Categoria, Giacenza, etc.)
- [ ] Status badges in Italian (Sotto scorta, OK, ecc.)

## Date Format Validation

- [ ] Date inputs show DD/MM/YYYY format
- [ ] Date pickers use Italian locale (giorni/mesi in italiano)
- [ ] Movement dates displayed as DD/MM/YYYY
- [ ] Export Excel uses DD/MM/YYYY format
- [ ] No MM/DD/YYYY or YYYY-MM-DD in user-facing displays

## Number Format Validation

- [ ] Decimal separator is comma (,) not dot (.)
- [ ] Thousands separator is dot (.) not comma (,)
- [ ] Example: 1234.56 displays as "1.234,56"
- [ ] Number inputs accept comma as decimal separator
- [ ] Quantity fields support format: "12,345" or "0,500"
- [ ] Min stock format: "10,000" instead of "10.000"

## Currency Format Validation

- [ ] Currency displays as "€ X.XXX,XX" (Euro symbol with space)
- [ ] Unit cost format: "€ 5,50" not "$5.50" or "5.50€"
- [ ] Total warehouse value format: "€ 12.345,67"
- [ ] Export Excel currency columns use "€X.XXX,XX" format
- [ ] No dollar signs ($) anywhere in the application

## Boolean Format Validation

- [ ] True values display as "Sì" not "Yes" or "true"
- [ ] False values display as "No" not "No" (check accent if applicable)
- [ ] Under stock indicator shows "Sì/No" in exports
- [ ] Checkbox labels in Italian

## Movement Type Labels

- [ ] IN movements labeled as "Carico" or "IN"
- [ ] OUT movements labeled as "Scarico" or "OUT"
- [ ] ADJUSTMENT movements labeled as "Rettifica" or "ADJUSTMENT"
- [ ] Movement type filters use Italian labels
- [ ] Export Excel shows "IN/OUT/ADJUSTMENT" (English acronyms OK, but context in Italian)

## Error Messages Validation

- [ ] 404 errors: "Articolo non trovato" (not "Item not found")
- [ ] 409 stock errors: "Giacenza insufficiente" or similar
- [ ] Validation errors: "La quantità deve essere maggiore di zero"
- [ ] Delete blocked: "Impossibile eliminare: giacenza non zero"
- [ ] Confirmation required: "Conferma richiesta per scarico"
- [ ] Adjustment note: "La nota è obbligatoria per le rettifiche"
- [ ] Date range errors in Italian
- [ ] Generic errors: "Si è verificato un errore"

## Confirmation Dialogs

- [ ] Delete confirmation: "Sei sicuro di voler eliminare..."
- [ ] OUT movement confirmation: "Stai per scaricare X unità di..."
- [ ] All "Yes/No" buttons show "Conferma/Annulla" or "Sì/No"

## Loading States

- [ ] Loading messages: "Caricamento in corso..." not "Loading..."
- [ ] Export loading: "Generazione Excel in corso..."
- [ ] Form submit: "Salvataggio..." or "Invio..."

## Excel Export Validation

- [ ] Sheet names in Italian: "Inventario", "Movimenti_ultimi_12_mesi"
- [ ] Column headers in Italian (see FR-026, FR-027)
- [ ] "Sotto Scorta" column shows "Sì/No"
- [ ] Numbers formatted with Italian locale (comma decimal)
- [ ] Dates formatted DD/MM/YYYY
- [ ] Currency formatted "€X.XXX,XX"

## Native Italian Speaker Review

- [ ] All strings reviewed by native Italian speaker
- [ ] Grammar and spelling checked
- [ ] Formal "tu" vs "lei" consistent (project uses informal "tu")
- [ ] Technical terms appropriate (giacenza, scarico, carico, rettifica)
- [ ] Error messages sound natural to Italian users
- [ ] Placeholder examples culturally appropriate

## Testing Checklist

- [ ] Test with Italian browser locale (it-IT)
- [ ] Test number input with comma separator
- [ ] Test date picker shows Italian month names
- [ ] Test Excel export opens in Italian Excel/LibreOffice
- [ ] Screenshot all pages and verify no English leaks
- [ ] Test all error scenarios and verify Italian messages
- [ ] Test all form validations show Italian errors

## Common Pitfalls to Check

- [ ] No "Submit" buttons (should be "Salva" or "Conferma")
- [ ] No "Delete" (should be "Elimina")
- [ ] No "Cancel" (should be "Annulla")
- [ ] No "Edit" (should be "Modifica")
- [ ] No "Search" (should be "Cerca")
- [ ] No "Filter" (should be "Filtra")
- [ ] No "Export" (should be "Esporta")
- [ ] No "Stock" without translation (should be "Giacenza")
- [ ] No "Loading..." (should be "Caricamento...")
- [ ] No "Error" standalone (should be "Errore" with context)

## Pre-Deployment Approval

**Validated By**: _________________
**Date**: _________________
**Native Italian Speaker**: [ ] Yes [ ] No
**All Items Checked**: [ ] Yes [ ] No
**Ready for Production**: [ ] Yes [ ] No

**Notes**:
_____________________________________________________________________
_____________________________________________________________________
