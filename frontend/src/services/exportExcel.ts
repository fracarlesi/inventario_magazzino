/**
 * Excel generation utility using SheetJS (xlsx) for client-side export.
 *
 * Tasks: T078, T079, T080
 * Requirements: FR-025, FR-026, FR-027, FR-028, FR-029
 */

import * as XLSX from 'xlsx';
import type { ItemWithStock, MovementDetail } from '@/types/api';

interface ExportData {
  export_date: string;
  period_start: string;
  period_end: string;
  inventory: ItemWithStock[];
  movements: MovementDetail[];
}

/**
 * Format number with Italian locale (comma decimal separator, dot thousands).
 * Example: 1234.56 -> "1.234,56"
 */
function formatNumberIT(value: number, decimals: number = 2): string {
  return value.toLocaleString('it-IT', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/**
 * Format currency with Italian locale.
 * Example: 1234.56 -> "€ 1.234,56"
 */
function formatCurrencyIT(value: number): string {
  return value.toLocaleString('it-IT', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

/**
 * Format date with Italian locale (DD/MM/YYYY).
 */
function formatDateIT(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('it-IT', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

/**
 * Format boolean as Italian "Sì"/"No".
 */
function formatBooleanIT(value: boolean): string {
  return value ? 'Sì' : 'No';
}

/**
 * Generate Excel workbook with Inventory and Movements sheets.
 *
 * @param exportData Data from /api/export/preview
 * @returns XLSX workbook ready for download
 */
export function generateExcel(exportData: ExportData): XLSX.WorkBook {
  // Create workbook
  const workbook = XLSX.utils.book_new();

  // ===== SHEET 1: Inventario =====
  // FR-026: Columns: Nome, Categoria, Unità, Giacenza, Min. Scorta, Sotto Scorta, Costo Unitario, Valore, Note
  const inventoryData = exportData.inventory.map((item) => ({
    'Nome': item.name,
    'Categoria': item.category || 'Senza categoria',
    'Unità': item.unit,
    'Giacenza': formatNumberIT(parseFloat(item.stock_quantity), 3), // Support up to 3 decimals
    'Min. Scorta': formatNumberIT(parseFloat(item.min_stock), 3),
    'Sotto Scorta': formatBooleanIT(item.is_under_min_stock),
    'Costo Unitario': formatCurrencyIT(parseFloat(item.unit_cost)),
    'Valore': formatCurrencyIT(parseFloat(item.stock_value)),
    'Note': item.notes || '',
  }));

  // Create inventory sheet
  const inventorySheet = XLSX.utils.json_to_sheet(inventoryData);

  // T079: Set column widths
  inventorySheet['!cols'] = [
    { wch: 30 }, // Nome
    { wch: 20 }, // Categoria
    { wch: 10 }, // Unità
    { wch: 12 }, // Giacenza
    { wch: 12 }, // Min. Scorta
    { wch: 12 }, // Sotto Scorta
    { wch: 15 }, // Costo Unitario
    { wch: 15 }, // Valore
    { wch: 40 }, // Note
  ];

  XLSX.utils.book_append_sheet(workbook, inventorySheet, 'Inventario');

  // ===== SHEET 2: Movimenti_ultimi_12_mesi =====
  // FR-027: Columns: Data, Articolo, Tipo, Quantità, Unità, Costo Unitario usato, Nota
  const movementsData = exportData.movements.map((movement) => ({
    'Data': formatDateIT(movement.movement_date),
    'Articolo': movement.item_name,
    'Tipo': movement.movement_type,
    'Quantità': formatNumberIT(parseFloat(movement.quantity), 3), // Show sign for ADJUSTMENT
    'Unità': '-', // Unit will be fetched from item if needed
    'Costo Unitario': movement.unit_cost_override
      ? formatCurrencyIT(parseFloat(movement.unit_cost_override))
      : '-',
    'Nota': movement.note || '',
  }));

  // Create movements sheet
  const movementsSheet = XLSX.utils.json_to_sheet(movementsData);

  // T079: Set column widths
  movementsSheet['!cols'] = [
    { wch: 12 }, // Data
    { wch: 30 }, // Articolo
    { wch: 12 }, // Tipo
    { wch: 12 }, // Quantità
    { wch: 10 }, // Unità
    { wch: 15 }, // Costo Unitario
    { wch: 50 }, // Nota
  ];

  XLSX.utils.book_append_sheet(workbook, movementsSheet, 'Movimenti_ultimi_12_mesi');

  return workbook;
}

/**
 * Generate Excel file and trigger browser download.
 *
 * @param exportData Data from /api/export/preview
 * @param filename Filename for download (default: magazzino_YYYYMMDD.xlsx)
 */
export function downloadExcel(exportData: ExportData, filename?: string): void {
  // T080: Generate filename with current date
  if (!filename) {
    const today = new Date();
    const dateStr = today.toISOString().split('T')[0].replace(/-/g, ''); // YYYYMMDD
    filename = `magazzino_${dateStr}.xlsx`;
  }

  // Generate workbook
  const workbook = generateExcel(exportData);

  // T080: Trigger browser download using SheetJS built-in method
  XLSX.writeFile(workbook, filename);
}
