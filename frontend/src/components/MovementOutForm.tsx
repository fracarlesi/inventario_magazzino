"use client";

import { useState } from "react";
import { NumericFormat } from "react-number-format";
import type { ItemWithStock } from "@/types/api";
import translations from "@/i18n/it.json";

const t = translations;

interface MovementOutFormProps {
  items: ItemWithStock[];
  onSubmit: (data: {
    item_id: string;
    quantity: string;
    movement_date: string;
    note?: string;
    confirmed: boolean;
  }) => Promise<void>;
  onCancel: () => void;
  isSubmitting?: boolean;
}

export default function MovementOutForm({
  items,
  onSubmit,
  onCancel,
  isSubmitting = false,
}: MovementOutFormProps) {
  const [selectedItemId, setSelectedItemId] = useState<string>("");
  const [quantity, setQuantity] = useState<string>("");
  const [movementDate, setMovementDate] = useState<string>(
    new Date().toISOString().split("T")[0]
  );
  const [note, setNote] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [showDropdown, setShowDropdown] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);

  // Validation and error state
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [apiError, setApiError] = useState<string>("");

  const selectedItem = items.find((item) => item.id === selectedItemId);

  // Filter items based on search term
  const filteredItems = items.filter((item) =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Validate form
  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!selectedItemId) {
      newErrors.item_id = "Seleziona un articolo";
    }

    const qty = parseFloat(quantity.replace(",", "."));
    if (!quantity || isNaN(qty) || qty <= 0) {
      newErrors.quantity = "La quantità deve essere maggiore di zero";
    }

    // FR-021: Max 3 decimal places
    const decimalPart = quantity.split(",")[1];
    if (decimalPart && decimalPart.length > 3) {
      newErrors.quantity = "Massimo 3 cifre decimali consentite";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    // FR-009: Show confirmation dialog before submitting
    setShowConfirmation(true);
  };

  const handleConfirmSubmit = async () => {
    setApiError("");

    const formData = {
      item_id: selectedItemId,
      quantity: quantity.replace(",", "."),
      movement_date: movementDate,
      note: note || undefined,
      confirmed: true, // FR-009: Confirmation required
    };

    try {
      await onSubmit(formData);
      setShowConfirmation(false);
    } catch (error: any) {
      // T047: Handle insufficient stock error
      setShowConfirmation(false);
      if (error.statusCode === 409) {
        setApiError(
          error.detail ||
            `Impossibile scaricare ${quantity} unità. Giacenza insufficiente.`
        );
      } else {
        setApiError("Errore durante la creazione del movimento");
      }
    }
  };

  const handleCancelConfirmation = () => {
    setShowConfirmation(false);
  };

  return (
    <>
      <form onSubmit={handleFormSubmit} className="space-y-6">
        <h3 className="text-lg font-medium text-gray-900">Scarico Merce (OUT)</h3>

        {/* API Error Display (T047) */}
        {apiError && (
          <div
            className="bg-red-50 border-l-4 border-red-400 p-4"
            role="alert"
          >
            <p className="text-sm text-red-700">{apiError}</p>
          </div>
        )}

        {/* Item Autocomplete */}
        <div>
          <label
            htmlFor="item-search-out"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Articolo *
          </label>
          <div className="relative">
            <input
              id="item-search-out"
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
                      setApiError(""); // Clear error on item change
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
            <p className="mt-1 text-sm text-gray-600">
              Giacenza disponibile:{" "}
              {parseFloat(selectedItem.stock_quantity).toFixed(2)}{" "}
              {selectedItem.unit}
            </p>
          )}
        </div>

        {/* Quantity */}
        <div>
          <label
            htmlFor="quantity-out"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Quantità da scaricare *
          </label>
          <NumericFormat
            id="quantity-out"
            className={`block w-full rounded-md border ${
              errors.quantity ? "border-red-500" : "border-gray-300"
            } px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500`}
            value={quantity}
            onValueChange={(values) => {
              setQuantity(values.value);
              setApiError(""); // Clear error on quantity change
            }}
            decimalSeparator=","
            thousandSeparator="."
            decimalScale={3}
            allowNegative={false}
            placeholder="0,000"
          />
          {errors.quantity && (
            <p className="mt-1 text-sm text-red-600">{errors.quantity}</p>
          )}
        </div>

        {/* Movement Date */}
        <div>
          <label
            htmlFor="movement-date-out"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Data Movimento
          </label>
          <input
            id="movement-date-out"
            type="date"
            className="block w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={movementDate}
            onChange={(e) => setMovementDate(e.target.value)}
          />
        </div>

        {/* Note */}
        <div>
          <label
            htmlFor="note-out"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Note (opzionale)
          </label>
          <textarea
            id="note-out"
            rows={3}
            className="block w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Es: Usato per riparazione Alfa Romeo 159"
          />
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
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50"
            disabled={isSubmitting}
          >
            Registra Scarico
          </button>
        </div>
      </form>

      {/* T046: Confirmation Dialog (FR-009) */}
      {showConfirmation && selectedItem && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75" />
          <div className="flex min-h-screen items-center justify-center p-4">
            <div className="relative w-full max-w-md transform rounded-lg bg-white p-6 shadow-xl">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Conferma Scarico
              </h3>
              <p className="text-sm text-gray-600 mb-6">
                Stai per scaricare{" "}
                <strong>
                  {quantity} {selectedItem.unit}
                </strong>{" "}
                di <strong>{selectedItem.name}</strong>.
                <br />
                Giacenza disponibile:{" "}
                <strong>
                  {parseFloat(selectedItem.stock_quantity).toFixed(2)}{" "}
                  {selectedItem.unit}
                </strong>
              </p>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={handleCancelConfirmation}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Annulla
                </button>
                <button
                  type="button"
                  onClick={handleConfirmSubmit}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "Salvataggio..." : "Conferma"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
