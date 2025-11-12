"use client";

import { useState, useMemo } from "react";
import { NumericFormat } from "react-number-format";
import type { ItemWithStock } from "@/types/api";
import translations from "@/i18n/it.json";

const t = translations;

interface AdjustmentFormProps {
  items: ItemWithStock[];
  onSubmit: (data: {
    item_id: string;
    target_stock: string;
    movement_date: string;
    note: string;
  }) => Promise<void>;
  onCancel: () => void;
  isSubmitting?: boolean;
}

export default function AdjustmentForm({
  items,
  onSubmit,
  onCancel,
  isSubmitting = false,
}: AdjustmentFormProps) {
  const [selectedItemId, setSelectedItemId] = useState<string>("");
  const [targetStock, setTargetStock] = useState<string>("");
  const [movementDate, setMovementDate] = useState<string>(
    new Date().toISOString().split("T")[0]
  );
  const [note, setNote] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [showDropdown, setShowDropdown] = useState(false);

  // Validation and error state
  const [errors, setErrors] = useState<Record<string, string>>({});

  const selectedItem = items.find((item) => item.id === selectedItemId);

  // Filter items based on search term
  const filteredItems = items.filter((item) =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // T065: Calculate delta in real-time (target - current)
  const calculatedDelta = useMemo(() => {
    if (!selectedItem || !targetStock) return null;

    const target = parseFloat(targetStock.replace(",", "."));
    const current = parseFloat(selectedItem.stock_quantity);

    if (isNaN(target) || isNaN(current)) return null;

    return target - current;
  }, [selectedItem, targetStock]);

  // Validate form (T066)
  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!selectedItemId) {
      newErrors.item_id = "Seleziona un articolo";
    }

    const target = parseFloat(targetStock.replace(",", "."));
    if (!targetStock || isNaN(target) || target < 0) {
      newErrors.target_stock = "La giacenza target deve essere >= 0";
    }

    // FR-021: Max 3 decimal places
    const decimalPart = targetStock.split(",")[1];
    if (decimalPart && decimalPart.length > 3) {
      newErrors.target_stock = "Massimo 3 cifre decimali consentite";
    }

    // FR-038: Target must differ from current
    if (calculatedDelta === 0) {
      newErrors.target_stock =
        "La giacenza target coincide con quella attuale. Nessuna rettifica necessaria.";
    }

    // FR-039: Note mandatory
    if (!note || !note.trim()) {
      newErrors.note =
        "La nota è obbligatoria per le rettifiche (spiega il motivo della discrepanza)";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    const formData = {
      item_id: selectedItemId,
      target_stock: targetStock.replace(",", "."),
      movement_date: movementDate,
      note: note.trim(),
    };

    await onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">
        Rettifica Inventario (ADJUSTMENT)
      </h3>

      <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
        <p className="text-sm text-blue-700">
          La rettifica serve per allineare la giacenza contabile con il conteggio
          fisico.
          <br />
          Inserisci la giacenza target desiderata, il sistema calcolerà
          automaticamente la quantità da aggiungere/sottrarre.
        </p>
      </div>

      {/* Item Autocomplete */}
      <div>
        <label
          htmlFor="item-search-adjustment"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Articolo *
        </label>
        <div className="relative">
          <input
            id="item-search-adjustment"
            type="text"
            className={`block w-full rounded-md border ${
              errors.item_id ? "border-red-500" : "border-gray-300"
            } px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500`}
            placeholder="Cerca articolo..."
            value={selectedItem ? selectedItem.name : searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setShowDropdown(true);
              if (selectedItemId) setSelectedItemId("");
            }}
            onFocus={() => setShowDropdown(true)}
          />

          {showDropdown && filteredItems.length > 0 && (
            <div className="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md py-1 text-base overflow-auto sm:text-sm border border-gray-300">
              {filteredItems.slice(0, 10).map((item) => (
                <div
                  key={item.id}
                  className="cursor-pointer select-none relative py-2 pl-3 pr-9 hover:bg-blue-50"
                  onClick={() => {
                    setSelectedItemId(item.id);
                    setSearchTerm("");
                    setShowDropdown(false);
                  }}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-gray-900">
                      {item.name}
                    </span>
                    <span className="text-sm text-gray-500">
                      Giacenza: {parseFloat(item.stock_quantity).toFixed(2)}{" "}
                      {item.unit}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        {errors.item_id && (
          <p className="mt-1 text-sm text-red-600">{errors.item_id}</p>
        )}
        {selectedItem && (
          <p className="mt-1 text-sm font-medium text-gray-700">
            Giacenza attuale: {parseFloat(selectedItem.stock_quantity).toFixed(2)}{" "}
            {selectedItem.unit}
          </p>
        )}
      </div>

      {/* Target Stock */}
      <div>
        <label
          htmlFor="target-stock"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Giacenza Target (desiderata) *
        </label>
        <NumericFormat
          id="target-stock"
          className={`block w-full rounded-md border ${
            errors.target_stock ? "border-red-500" : "border-gray-300"
          } px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500`}
          value={targetStock}
          onValueChange={(values) => setTargetStock(values.value)}
          decimalSeparator=","
          thousandSeparator="."
          decimalScale={3}
          allowNegative={false}
          placeholder="0,000"
        />
        {errors.target_stock && (
          <p className="mt-1 text-sm text-red-600">{errors.target_stock}</p>
        )}

        {/* T065: Delta calculation preview (FR-037, FR-040) */}
        {calculatedDelta !== null && calculatedDelta !== 0 && (
          <div
            className={`mt-2 p-3 rounded-md ${
              calculatedDelta > 0
                ? "bg-green-50 border-l-4 border-green-400"
                : "bg-red-50 border-l-4 border-red-400"
            }`}
          >
            <p
              className={`text-sm font-medium ${
                calculatedDelta > 0 ? "text-green-700" : "text-red-700"
              }`}
            >
              {calculatedDelta > 0 ? "Rettifica: +" : "Rettifica: "}
              {Math.abs(calculatedDelta).toFixed(3)} {selectedItem?.unit}
            </p>
            <p className="text-xs text-gray-600 mt-1">
              {calculatedDelta > 0
                ? "Verrà aggiunta giacenza"
                : "Verrà sottratta giacenza"}
            </p>
          </div>
        )}
      </div>

      {/* Movement Date */}
      <div>
        <label
          htmlFor="movement-date-adjustment"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Data Rettifica
        </label>
        <input
          id="movement-date-adjustment"
          type="date"
          className="block w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={movementDate}
          onChange={(e) => setMovementDate(e.target.value)}
        />
      </div>

      {/* Note (FR-039: Mandatory) */}
      <div>
        <label
          htmlFor="note-adjustment"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Nota Obbligatoria *
        </label>
        <textarea
          id="note-adjustment"
          rows={4}
          className={`block w-full rounded-md border ${
            errors.note ? "border-red-500" : "border-gray-300"
          } px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500`}
          value={note}
          onChange={(e) => setNote(e.target.value)}
          placeholder="Es: Conteggio fisico mensile - 2 unità danneggiate trovate in magazzino"
        />
        {errors.note && (
          <p className="mt-1 text-sm text-red-600">{errors.note}</p>
        )}
        <p className="mt-1 text-xs text-gray-500">
          Spiega il motivo della discrepanza tra giacenza contabile e fisica
        </p>
      </div>

      {/* Actions */}
      <div className="flex justify-end space-x-3">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
          disabled={isSubmitting}
        >
          Annulla
        </button>
        <button
          type="submit"
          className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-yellow-600 hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-yellow-500 disabled:opacity-50"
          disabled={isSubmitting || calculatedDelta === 0}
        >
          {isSubmitting ? "Salvataggio..." : "Registra Rettifica"}
        </button>
      </div>
    </form>
  );
}
