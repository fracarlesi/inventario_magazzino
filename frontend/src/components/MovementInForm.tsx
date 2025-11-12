"use client";

import { useState, useEffect } from "react";
import { NumericFormat } from "react-number-format";
import type { ItemWithStock } from "@/types/api";
import translations from "@/i18n/it.json";

const t = translations;

interface MovementInFormProps {
  items: ItemWithStock[];
  onSubmit: (data: {
    item_id: string;
    quantity: string;
    movement_date: string;
    unit_cost_override?: string;
    note?: string;
  }) => Promise<void>;
  onCancel: () => void;
  isSubmitting?: boolean;
}

export default function MovementInForm({
  items,
  onSubmit,
  onCancel,
  isSubmitting = false,
}: MovementInFormProps) {
  const [selectedItemId, setSelectedItemId] = useState<string>("");
  const [quantity, setQuantity] = useState<string>("");
  const [movementDate, setMovementDate] = useState<string>(
    new Date().toISOString().split("T")[0] // Today's date in YYYY-MM-DD
  );
  const [unitCostOverride, setUnitCostOverride] = useState<string>("");
  const [note, setNote] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [showDropdown, setShowDropdown] = useState(false);

  // T039: Client-side validation state
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Filter items based on search term (T038: autocomplete)
  const filteredItems = items.filter((item) =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const selectedItem = items.find((item) => item.id === selectedItemId);

  // Validate form
  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    // FR-020: Item required
    if (!selectedItemId) {
      newErrors.item_id = "Seleziona un articolo";
    }

    // FR-019: Quantity > 0
    const qty = parseFloat(quantity.replace(",", "."));
    if (!quantity || isNaN(qty) || qty <= 0) {
      newErrors.quantity = "La quantità deve essere maggiore di zero";
    }

    // FR-021: Max 3 decimal places
    const decimalPart = quantity.split(",")[1];
    if (decimalPart && decimalPart.length > 3) {
      newErrors.quantity = "Massimo 3 cifre decimali consentite";
    }

    // Unit cost override validation (if provided)
    if (unitCostOverride) {
      const cost = parseFloat(unitCostOverride.replace(",", "."));
      if (isNaN(cost) || cost < 0) {
        newErrors.unit_cost_override = "Il costo deve essere maggiore o uguale a zero";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    // Convert Italian format to API format (comma to dot)
    const formData = {
      item_id: selectedItemId,
      quantity: quantity.replace(",", "."),
      movement_date: movementDate,
      unit_cost_override: unitCostOverride
        ? unitCostOverride.replace(",", ".")
        : undefined,
      note: note || undefined,
    };

    await onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Carico Merce (IN)</h3>

      {/* Item Autocomplete (T038) */}
      <div>
        <label
          htmlFor="item-search"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Articolo *
        </label>
        <div className="relative">
          <input
            id="item-search"
            type="text"
            className={`block w-full rounded-md border ${
              errors.item_id ? "border-red-500" : "border-gray-300"
            } px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500`}
            placeholder="Cerca articolo..."
            value={selectedItem ? selectedItem.name : searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setShowDropdown(true);
              if (selectedItemId) setSelectedItemId(""); // Clear selection
            }}
            onFocus={() => setShowDropdown(true)}
            aria-invalid={errors.item_id ? "true" : "false"}
          />

          {/* Dropdown */}
          {showDropdown && filteredItems.length > 0 && (
            <div className="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md py-1 text-base overflow-auto focus:outline-none sm:text-sm border border-gray-300">
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
                  {item.category && (
                    <span className="text-xs text-gray-500">
                      {item.category}
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
        {errors.item_id && (
          <p className="mt-1 text-sm text-red-600">{errors.item_id}</p>
        )}
        {selectedItem && (
          <p className="mt-1 text-sm text-gray-600">
            Giacenza attuale: {parseFloat(selectedItem.stock_quantity).toFixed(2)}{" "}
            {selectedItem.unit}
          </p>
        )}
      </div>

      {/* Quantity with Italian formatting (FR-021) */}
      <div>
        <label
          htmlFor="quantity"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Quantità *
        </label>
        <NumericFormat
          id="quantity"
          className={`block w-full rounded-md border ${
            errors.quantity ? "border-red-500" : "border-gray-300"
          } px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500`}
          value={quantity}
          onValueChange={(values) => setQuantity(values.value)}
          decimalSeparator=","
          thousandSeparator="."
          decimalScale={3}
          allowNegative={false}
          placeholder="0,000"
          aria-invalid={errors.quantity ? "true" : "false"}
        />
        {errors.quantity && (
          <p className="mt-1 text-sm text-red-600">{errors.quantity}</p>
        )}
      </div>

      {/* Movement Date */}
      <div>
        <label
          htmlFor="movement-date"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Data Movimento
        </label>
        <input
          id="movement-date"
          type="date"
          className="block w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={movementDate}
          onChange={(e) => setMovementDate(e.target.value)}
        />
      </div>

      {/* Unit Cost Override (FR-010) */}
      <div>
        <label
          htmlFor="unit-cost"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Costo Unitario (opzionale - sovrascrive il costo dell'articolo)
        </label>
        <div className="relative">
          <span className="absolute left-3 top-2 text-gray-500">€</span>
          <NumericFormat
            id="unit-cost"
            className={`block w-full rounded-md border ${
              errors.unit_cost_override ? "border-red-500" : "border-gray-300"
            } pl-8 pr-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500`}
            value={unitCostOverride}
            onValueChange={(values) => setUnitCostOverride(values.value)}
            decimalSeparator=","
            thousandSeparator="."
            decimalScale={2}
            allowNegative={false}
            placeholder="0,00"
            aria-invalid={errors.unit_cost_override ? "true" : "false"}
          />
        </div>
        {errors.unit_cost_override && (
          <p className="mt-1 text-sm text-red-600">
            {errors.unit_cost_override}
          </p>
        )}
      </div>

      {/* Note */}
      <div>
        <label
          htmlFor="note"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Note (opzionale)
        </label>
        <textarea
          id="note"
          rows={3}
          className="block w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={note}
          onChange={(e) => setNote(e.target.value)}
          placeholder="Es: Fornitore XYZ, Fattura n. 123"
        />
      </div>

      {/* Actions */}
      <div className="flex justify-end space-x-3">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isSubmitting}
        >
          Annulla
        </button>
        <button
          type="submit"
          className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={isSubmitting}
        >
          {isSubmitting ? "Salvataggio..." : "Registra Carico"}
        </button>
      </div>
    </form>
  );
}
