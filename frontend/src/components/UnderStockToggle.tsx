"use client";

import translations from "@/i18n/it.json";

const t = translations.dashboard.filters.under_stock;

interface UnderStockToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
}

export default function UnderStockToggle({
  checked,
  onChange,
}: UnderStockToggleProps) {
  return (
    <div className="flex items-center">
      <input
        id="under-stock-toggle"
        type="checkbox"
        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
      />
      <label
        htmlFor="under-stock-toggle"
        className="ml-2 block text-sm text-gray-900 cursor-pointer"
        title={t.tooltip}
      >
        {t.label}
      </label>
    </div>
  );
}
