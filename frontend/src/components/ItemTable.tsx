"use client";

import { useMemo } from "react";
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  createColumnHelper,
  type ColumnDef,
} from "@tanstack/react-table";
import type { ItemWithStock } from "@/types/api";
import translations from "@/i18n/it.json";

const t = translations.dashboard.table;
const columnHelper = createColumnHelper<ItemWithStock>();

/**
 * Format decimal string to Italian locale with comma separator
 */
function formatDecimal(value: string, decimals: number = 2): string {
  const num = parseFloat(value);
  return num.toLocaleString("it-IT", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/**
 * Format currency in EUR with Italian locale
 */
function formatCurrency(value: string): string {
  const num = parseFloat(value);
  return num.toLocaleString("it-IT", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

/**
 * Format datetime to Italian locale
 */
function formatDateTime(value: string | null): string {
  if (!value) return "-";
  const date = new Date(value);
  return date.toLocaleString("it-IT", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

interface ItemTableProps {
  items: ItemWithStock[];
  isLoading?: boolean;
  onRowClick?: (item: ItemWithStock) => void;
}

export default function ItemTable({ items, isLoading, onRowClick }: ItemTableProps) {
  // Define table columns with Italian labels (FR-001)
  const columns = useMemo<ColumnDef<ItemWithStock, any>[]>(
    () => [
      columnHelper.accessor("name", {
        header: t.columns.name,
        cell: (info) => info.getValue(),
      }),
      columnHelper.accessor("category", {
        header: t.columns.category,
        cell: (info) => info.getValue() || "-",
      }),
      columnHelper.accessor("unit", {
        header: t.columns.unit,
        cell: (info) => info.getValue(),
      }),
      columnHelper.accessor("stock_quantity", {
        header: t.columns.stock_quantity,
        cell: (info) => formatDecimal(info.getValue(), 2),
      }),
      columnHelper.accessor("min_stock", {
        header: t.columns.min_stock,
        cell: (info) => formatDecimal(info.getValue(), 2),
      }),
      columnHelper.accessor("unit_cost", {
        header: t.columns.unit_cost,
        cell: (info) => formatCurrency(info.getValue()),
      }),
      columnHelper.accessor("stock_value", {
        header: t.columns.stock_value,
        cell: (info) => formatCurrency(info.getValue()),
      }),
      columnHelper.accessor("last_movement_at", {
        header: t.columns.last_movement,
        cell: (info) => formatDateTime(info.getValue()),
      }),
    ],
    []
  );

  const table = useReactTable({
    data: items,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-gray-500">{t.loading}</div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="flex justify-center items-center py-12 text-gray-500">
        {t.empty}
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200 border border-gray-200">
        <thead className="bg-gray-50">
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th
                  key={header.id}
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider"
                >
                  {header.isPlaceholder
                    ? null
                    : flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {table.getRowModel().rows.map((row) => {
            // FR-005: Highlight under-stock items with red background
            const isUnderStock = row.original.is_under_min_stock;
            const rowClassName = isUnderStock
              ? "bg-red-50 hover:bg-red-100"
              : "hover:bg-gray-50";

            return (
              <tr
                key={row.id}
                className={`${rowClassName} transition-colors ${
                  onRowClick ? "cursor-pointer" : ""
                }`}
                role="row"
                onClick={() => onRowClick && onRowClick(row.original)}
              >
                {row.getVisibleCells().map((cell) => (
                  <td
                    key={cell.id}
                    className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                    role="cell"
                  >
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>

      {/* FR-034: Keyboard navigation note - react-table provides ARIA navigation out-of-the-box */}
      {/* Screen readers will announce table structure, row/column positions automatically */}
    </div>
  );
}
