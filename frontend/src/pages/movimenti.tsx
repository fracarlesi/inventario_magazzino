"use client";

import { useState } from "react";
import useSWR from "swr";
import { fetchMovements } from "@/services/api";
import translations from "@/i18n/it.json";

const t = translations;

export default function MovimentiPage() {
  const [fromDate, setFromDate] = useState(() => {
    const date = new Date();
    date.setDate(date.getDate() - 30);
    return date.toISOString().split("T")[0];
  });
  const [toDate, setToDate] = useState(new Date().toISOString().split("T")[0]);
  const [movementType, setMovementType] = useState("All");

  // Fetch movements with SWR
  const { data, isLoading } = useSWR(
    `/movements?from=${fromDate}&to=${toDate}&type=${movementType}`,
    () =>
      fetchMovements({
        from_date: fromDate,
        to_date: toDate,
        movement_type: movementType === "All" ? undefined : movementType,
        limit: 100,
      })
  );

  const movements = data?.movements || [];

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Storico Movimenti
        </h1>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Data Inizio
              </label>
              <input
                type="date"
                className="block w-full rounded-md border border-gray-300 px-3 py-2"
                value={fromDate}
                onChange={(e) => setFromDate(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Data Fine
              </label>
              <input
                type="date"
                className="block w-full rounded-md border border-gray-300 px-3 py-2"
                value={toDate}
                onChange={(e) => setToDate(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tipo Movimento
              </label>
              <select
                className="block w-full rounded-md border border-gray-300 px-3 py-2"
                value={movementType}
                onChange={(e) => setMovementType(e.target.value)}
              >
                <option value="All">Tutti</option>
                <option value="IN">Carico (IN)</option>
                <option value="OUT">Scarico (OUT)</option>
                <option value="ADJUSTMENT">Rettifica</option>
              </select>
            </div>
          </div>
        </div>

        {/* Movements Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {isLoading ? (
            <div className="p-12 text-center text-gray-500">
              Caricamento...
            </div>
          ) : movements.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              Nessun movimento trovato
            </div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                    Data
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                    Articolo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                    Tipo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                    Quantità
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                    Nota
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {movements.map((movement: any) => (
                  <tr key={movement.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(movement.movement_date).toLocaleDateString("it-IT")}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {movement.item_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          movement.movement_type === "IN"
                            ? "bg-green-100 text-green-800"
                            : movement.movement_type === "OUT"
                            ? "bg-red-100 text-red-800"
                            : "bg-yellow-100 text-yellow-800"
                        }`}
                      >
                        {movement.movement_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {parseFloat(movement.quantity).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {movement.note || "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="mt-4 text-sm text-gray-600">
          Totale movimenti: {data?.total || 0}
        </div>
      </div>
    </div>
  );
}
