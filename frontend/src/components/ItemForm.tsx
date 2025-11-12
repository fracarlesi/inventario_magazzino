"use client";

import { useState, useEffect } from "react";
import { NumericFormat } from "react-number-format";
import type { ItemWithStock } from "@/types/api";
import translations from "@/i18n/it.json";

const t = translations;

interface ItemFormProps {
  item?: ItemWithStock; // If provided, edit mode
  onSubmit: (data: {
    name: string;
    category?: string;
    unit: string;
    notes?: string;
    min_stock: string;
    unit_cost: string;
  }) => Promise<void>;
  onCancel: () => void;
  onDelete?: () => Promise<void>; // Only for edit mode
  isSubmitting?: boolean;
  categories?: string[]; // For autocomplete
  units?: string[]; // For autocomplete
}

export default function ItemForm({
  item,
  onSubmit,
  onCancel,
  onDelete,
  isSubmitting = false,
  categories = [],
  units = [],
}: ItemFormProps) {
  const isEditMode = !!item;

  // Form state
  const [name, setName] = useState(item?.name || "");
  const [category, setCategory] = useState(item?.category || "");
  const [unit, setUnit] = useState(item?.unit || "pz");
  const [notes, setNotes] = useState(item?.notes || "");
  const [minStock, setMinStock] = useState(
    item ? parseFloat(item.min_stock).toString() : "0"
  );
  const [unitCost, setUnitCost] = useState(
    item ? parseFloat(item.unit_cost).toString() : "0"
  );

  // Autocomplete state
  const [showCategoryDropdown, setShowCategoryDropdown] = useState(false);
  const [showUnitDropdown, setShowUnitDropdown] = useState(false);
  const [categorySearch, setCategorySearch] = useState("");
  const [unitSearch, setUnitSearch] = useState("");

  // Validation state
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Filter categories/units based on search
  const filteredCategories = categories.filter((cat) =>
    cat.toLowerCase().includes(categorySearch.toLowerCase())
  );

  const filteredUnits = units.filter((u) =>
    u.toLowerCase().includes(unitSearch.toLowerCase())
  );

  // Common units if none exist yet
  const commonUnits = ["pz", "kg", "lt", "m", "kit", "set"];
  const displayUnits = filteredUnits.length > 0 ? filteredUnits : commonUnits;

  // Validate form
  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    // FR-020: Name required
    if (!name || !name.trim()) {
      newErrors.name = "Il nome dell'articolo non può essere vuoto";
    }

    // Unit required
    if (!unit || !unit.trim()) {
      newErrors.unit = "L'unità di misura è obbligatoria";
    }

    // FR-021: Numeric validation
    const minStockNum = parseFloat(minStock.replace(",", "."));
    if (isNaN(minStockNum) || minStockNum < 0) {
      newErrors.min_stock = "La scorta minima deve essere >= 0";
    }

    const unitCostNum = parseFloat(unitCost.replace(",", "."));
    if (isNaN(unitCostNum) || unitCostNum < 0) {
      newErrors.unit_cost = "Il costo unitario deve essere >= 0";
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
      name: name.trim(),
      category: category.trim() || undefined,
      unit: unit.trim(),
      notes: notes.trim() || undefined,
      min_stock: minStock.replace(",", "."),
      unit_cost: unitCost.replace(",", "."),
    };

    await onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">
        {isEditMode ? "Modifica Articolo" : "Nuovo Articolo"}
      </h3>

      {/* Name */}
      <div>
        <label
          htmlFor="item-name"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Nome Articolo *
        </label>
        <input
          id="item-name"
          type="text"
          className={`block w-full rounded-md border ${
            errors.name ? "border-red-500" : "border-gray-300"
          } px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500`}
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Es: Olio motore 5W30"
        />
        {errors.name && (
          <p className="mt-1 text-sm text-red-600">{errors.name}</p>
        )}
      </div>

      {/* Category with autocomplete (T056) */}
      <div>
        <label
          htmlFor="item-category"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Categoria (opzionale)
        </label>
        <div className="relative">
          <input
            id="item-category"
            type="text"
            className="block w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={category}
            onChange={(e) => {
              setCategory(e.target.value);
              setCategorySearch(e.target.value);
              setShowCategoryDropdown(true);
            }}
            onFocus={() => setShowCategoryDropdown(true)}
            placeholder="Es: Filtri olio"
          />

          {showCategoryDropdown && filteredCategories.length > 0 && (
            <div className="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-48 rounded-md py-1 text-base overflow-auto sm:text-sm border border-gray-300">
              {filteredCategories.map((cat) => (
                <div
                  key={cat}
                  className="cursor-pointer select-none py-2 pl-3 pr-9 hover:bg-blue-50"
                  onClick={() => {
                    setCategory(cat);
                    setShowCategoryDropdown(false);
                  }}
                >
                  {cat}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Unit with autocomplete (T057) */}
      <div>
        <label
          htmlFor="item-unit"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Unità di Misura *
        </label>
        <div className="relative">
          <input
            id="item-unit"
            type="text"
            className={`block w-full rounded-md border ${
              errors.unit ? "border-red-500" : "border-gray-300"
            } px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500`}
            value={unit}
            onChange={(e) => {
              setUnit(e.target.value);
              setUnitSearch(e.target.value);
              setShowUnitDropdown(true);
            }}
            onFocus={() => setShowUnitDropdown(true)}
            placeholder="Es: pz, kg, lt"
          />

          {showUnitDropdown && displayUnits.length > 0 && (
            <div className="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-48 rounded-md py-1 text-base overflow-auto sm:text-sm border border-gray-300">
              {displayUnits.map((u) => (
                <div
                  key={u}
                  className="cursor-pointer select-none py-2 pl-3 pr-9 hover:bg-blue-50"
                  onClick={() => {
                    setUnit(u);
                    setShowUnitDropdown(false);
                  }}
                >
                  {u}
                </div>
              ))}
            </div>
          )}
        </div>
        {errors.unit && (
          <p className="mt-1 text-sm text-red-600">{errors.unit}</p>
        )}
      </div>

      {/* Min Stock */}
      <div>
        <label
          htmlFor="item-min-stock"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Scorta Minima
        </label>
        <NumericFormat
          id="item-min-stock"
          className={`block w-full rounded-md border ${
            errors.min_stock ? "border-red-500" : "border-gray-300"
          } px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500`}
          value={minStock}
          onValueChange={(values) => setMinStock(values.value)}
          decimalSeparator=","
          thousandSeparator="."
          decimalScale={3}
          allowNegative={false}
          placeholder="0,000"
        />
        {errors.min_stock && (
          <p className="mt-1 text-sm text-red-600">{errors.min_stock}</p>
        )}
      </div>

      {/* Unit Cost */}
      <div>
        <label
          htmlFor="item-unit-cost"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Costo Unitario (€)
        </label>
        <NumericFormat
          id="item-unit-cost"
          className={`block w-full rounded-md border ${
            errors.unit_cost ? "border-red-500" : "border-gray-300"
          } px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500`}
          value={unitCost}
          onValueChange={(values) => setUnitCost(values.value)}
          decimalSeparator=","
          thousandSeparator="."
          decimalScale={2}
          allowNegative={false}
          placeholder="0,00"
          prefix="€ "
        />
        {errors.unit_cost && (
          <p className="mt-1 text-sm text-red-600">{errors.unit_cost}</p>
        )}
      </div>

      {/* Notes */}
      <div>
        <label
          htmlFor="item-notes"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Note (opzionale)
        </label>
        <textarea
          id="item-notes"
          rows={3}
          className="block w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Es: Formato universale, compatibile con..."
        />
      </div>

      {/* Actions */}
      <div className="flex justify-between">
        <div>
          {isEditMode && onDelete && (
            <button
              type="button"
              onClick={onDelete}
              className="px-4 py-2 border border-red-300 rounded-md text-sm font-medium text-red-700 hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500"
              disabled={isSubmitting}
            >
              Elimina
            </button>
          )}
        </div>
        <div className="flex space-x-3">
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
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Salvataggio..." : isEditMode ? "Salva" : "Crea Articolo"}
          </button>
        </div>
      </div>
    </form>
  );
}
