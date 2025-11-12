"use client";

import { useState, useMemo, useCallback } from "react";
import useSWR from "swr";
import type { ItemWithStock, DashboardStats as StatsType } from "@/types/api";
import {
  fetchItems,
  fetchDashboardStats,
  createMovement,
  createItem,
  updateItem,
  deleteItem,
  fetchCategories,
  fetchExportData,
} from "@/services/api";
import { downloadExcel } from "@/services/exportExcel";
import ItemTable from "@/components/ItemTable";
import SearchBar from "@/components/SearchBar";
import CategoryFilter from "@/components/CategoryFilter";
import UnderStockToggle from "@/components/UnderStockToggle";
import DashboardStats from "@/components/DashboardStats";
import Modal from "@/components/Modal";
import MovementInForm from "@/components/MovementInForm";
import MovementOutForm from "@/components/MovementOutForm";
import AdjustmentForm from "@/components/AdjustmentForm";
import ItemForm from "@/components/ItemForm";
import translations from "@/i18n/it.json";

const t = translations.dashboard;

export default function DashboardPage() {
  // Filter state
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [underStockOnly, setUnderStockOnly] = useState(false);

  // Modal state
  const [isInModalOpen, setIsInModalOpen] = useState(false);
  const [isOutModalOpen, setIsOutModalOpen] = useState(false);
  const [isAdjustmentModalOpen, setIsAdjustmentModalOpen] = useState(false);
  const [isItemModalOpen, setIsItemModalOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<ItemWithStock | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  // Autocomplete data
  const [categories_list, setCategories] = useState<string[]>([]);
  const [units_list, setUnits] = useState<string[]>(["pz", "kg", "lt", "m", "kit"]);

  // Build SWR key based on filters for automatic revalidation
  const itemsKey = useMemo(() => {
    const params = new URLSearchParams();
    if (searchQuery) params.set("search", searchQuery);
    if (selectedCategory) params.set("category", selectedCategory);
    if (underStockOnly) params.set("under_stock_only", "true");
    return `/items?${params.toString()}`;
  }, [searchQuery, selectedCategory, underStockOnly]);

  // Fetch items with SWR (automatic revalidation on focus/reconnect)
  const {
    data: items,
    error: itemsError,
    isLoading: itemsLoading,
  } = useSWR<ItemWithStock[]>(itemsKey, () =>
    fetchItems({
      search: searchQuery || undefined,
      category: selectedCategory || undefined,
      under_stock_only: underStockOnly,
      sort_by: "name",
      sort_order: "asc",
    })
  );

  // Fetch dashboard stats with SWR
  const {
    data: stats,
    error: statsError,
    isLoading: statsLoading,
  } = useSWR<StatsType>("/dashboard/stats", fetchDashboardStats);

  // Extract unique categories from items for filter dropdown
  const categories = useMemo(() => {
    if (!items) return [];
    const uniqueCategories = new Set<string>();
    items.forEach((item) => {
      if (item.category) uniqueCategories.add(item.category);
    });
    return Array.from(uniqueCategories).sort();
  }, [items]);

  // Handlers
  const handleSearchChange = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  const handleCategoryChange = useCallback((category: string | null) => {
    setSelectedCategory(category);
  }, []);

  const handleUnderStockToggle = useCallback((checked: boolean) => {
    setUnderStockOnly(checked);
  }, []);

  // Handle IN movement submission
  const handleInMovementSubmit = useCallback(
    async (data: any) => {
      setIsSubmitting(true);
      try {
        await createMovement(data);
        // Success: close modal and refresh items
        setIsInModalOpen(false);
        // Revalidate both items and stats
        await Promise.all([
          fetch(`/api${itemsKey}`).then(() => {}),
          fetch("/api/dashboard/stats").then(() => {}),
        ]);
        // Trigger SWR revalidation
        window.location.reload(); // Simple solution for now
      } catch (error) {
        console.error("Error creating movement:", error);
        alert("Errore durante la creazione del movimento");
      } finally {
        setIsSubmitting(false);
      }
    },
    [itemsKey]
  );

  // Handle OUT movement submission
  const handleOutMovementSubmit = useCallback(
    async (data: any) => {
      setIsSubmitting(true);
      try {
        await createMovement(data);
        // Success: close modal and refresh items
        setIsOutModalOpen(false);
        // Revalidate
        window.location.reload();
      } catch (error: any) {
        console.error("Error creating OUT movement:", error);
        // Let the MovementOutForm component handle the error display
        throw error;
      } finally {
        setIsSubmitting(false);
      }
    },
    []
  );

  // Handle item create/update
  const handleItemSubmit = useCallback(
    async (data: any) => {
      setIsSubmitting(true);
      try {
        if (selectedItem) {
          // Update existing item
          await updateItem(selectedItem.id, data);
        } else {
          // Create new item
          await createItem(data);
        }
        // Success: close modal and refresh
        setIsItemModalOpen(false);
        setSelectedItem(null);
        window.location.reload();
      } catch (error: any) {
        console.error("Error saving item:", error);
        alert("Errore durante il salvataggio dell'articolo");
      } finally {
        setIsSubmitting(false);
      }
    },
    [selectedItem]
  );

  // Handle item delete with confirmation (T059)
  const handleItemDelete = useCallback(async () => {
    if (!selectedItem) return;

    setShowDeleteConfirm(true);
  }, [selectedItem]);

  const confirmDelete = useCallback(async () => {
    if (!selectedItem) return;

    setIsSubmitting(true);
    try {
      await deleteItem(selectedItem.id);
      // Success
      setShowDeleteConfirm(false);
      setIsItemModalOpen(false);
      setSelectedItem(null);
      window.location.reload();
    } catch (error: any) {
      console.error("Error deleting item:", error);
      setShowDeleteConfirm(false);
      // Show error message from backend (FR-015, FR-016, FR-017)
      alert(
        error.detail ||
          "Impossibile eliminare l'articolo. Verifica che la giacenza sia zero e che non ci siano movimenti recenti."
      );
    } finally {
      setIsSubmitting(false);
    }
  }, [selectedItem]);

  // Open item form for creation
  const handleNewItem = useCallback(() => {
    setSelectedItem(null);
    setIsItemModalOpen(true);
    // Fetch categories for autocomplete
    fetchCategories().then(setCategories).catch(console.error);
  }, []);

  // Open item form for editing
  const handleEditItem = useCallback((item: ItemWithStock) => {
    setSelectedItem(item);
    setIsItemModalOpen(true);
    // Fetch categories for autocomplete
    fetchCategories().then(setCategories).catch(console.error);
  }, []);

  // Handle adjustment submission
  const handleAdjustmentSubmit = useCallback(
    async (data: any) => {
      setIsSubmitting(true);
      try {
        await createMovement(data);
        // Success: close modal and refresh
        setIsAdjustmentModalOpen(false);
        window.location.reload();
      } catch (error: any) {
        console.error("Error creating adjustment:", error);
        alert("Errore durante la rettifica");
      } finally {
        setIsSubmitting(false);
      }
    },
    []
  );

  // Handle Excel export (T080)
  const handleExport = useCallback(async () => {
    setIsExporting(true);
    try {
      const exportData = await fetchExportData();
      downloadExcel(exportData);
      // Show success message (optional)
      console.log(t.export_success);
    } catch (error: any) {
      console.error("Error exporting Excel:", error);
      alert(t.export_error);
    } finally {
      setIsExporting(false);
    }
  }, []);

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <header className="mb-8 flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900">{t.title}</h1>
          <div className="flex space-x-3">
            <button
              onClick={handleExport}
              disabled={isExporting}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
              title={t.export_button}
            >
              {isExporting ? t.export_loading : "📊 " + t.export_button}
            </button>
            <button
              onClick={handleNewItem}
              className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
            >
              + Nuovo Articolo
            </button>
            <button
              onClick={() => setIsInModalOpen(true)}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
            >
              + Carico (IN)
            </button>
            <button
              onClick={() => setIsOutModalOpen(true)}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            >
              - Scarico (OUT)
            </button>
            <button
              onClick={() => setIsAdjustmentModalOpen(true)}
              className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2"
            >
              ⚖ Rettifica
            </button>
          </div>
        </header>

        {/* Dashboard Statistics (FR-041, FR-042) */}
        <section className="mb-8" aria-label="Statistiche magazzino">
          <DashboardStats stats={stats || null} isLoading={statsLoading} />
        </section>

        {/* Filters Section */}
        <section
          className="bg-white rounded-lg shadow p-6 mb-6"
          aria-label="Filtri inventario"
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search Bar (FR-002) */}
            <SearchBar onSearch={handleSearchChange} />

            {/* Category Filter (FR-003) */}
            <CategoryFilter
              categories={categories}
              selectedCategory={selectedCategory}
              onCategoryChange={handleCategoryChange}
            />

            {/* Under Stock Toggle (FR-004) */}
            <div className="flex items-end">
              <UnderStockToggle
                checked={underStockOnly}
                onChange={handleUnderStockToggle}
              />
            </div>
          </div>
        </section>

        {/* Items Table (FR-001, FR-005) */}
        <section className="bg-white rounded-lg shadow overflow-hidden" aria-label="Inventario articoli">
          {itemsError && (
            <div
              className="bg-red-50 border-l-4 border-red-400 p-4 mb-4"
              role="alert"
            >
              <p className="text-sm text-red-700">
                {translations.errors.generic}
              </p>
            </div>
          )}

          <ItemTable
            items={items || []}
            isLoading={itemsLoading}
            onRowClick={handleEditItem}
          />
        </section>

        {/* Footer with active filter info */}
        {(searchQuery || selectedCategory || underStockOnly) && (
          <div className="mt-4 text-sm text-gray-600">
            Filtri attivi:
            {searchQuery && ` Ricerca: "${searchQuery}"`}
            {selectedCategory && ` | Categoria: ${selectedCategory}`}
            {underStockOnly && ` | Solo sotto scorta`}
          </div>
        )}

        {/* IN Movement Modal */}
        <Modal
          isOpen={isInModalOpen}
          onClose={() => setIsInModalOpen(false)}
          maxWidth="xl"
        >
          <MovementInForm
            items={items || []}
            onSubmit={handleInMovementSubmit}
            onCancel={() => setIsInModalOpen(false)}
            isSubmitting={isSubmitting}
          />
        </Modal>

        {/* OUT Movement Modal */}
        <Modal
          isOpen={isOutModalOpen}
          onClose={() => setIsOutModalOpen(false)}
          maxWidth="xl"
        >
          <MovementOutForm
            items={items || []}
            onSubmit={handleOutMovementSubmit}
            onCancel={() => setIsOutModalOpen(false)}
            isSubmitting={isSubmitting}
          />
        </Modal>

        {/* Item Create/Edit Modal (T058) */}
        <Modal
          isOpen={isItemModalOpen}
          onClose={() => {
            setIsItemModalOpen(false);
            setSelectedItem(null);
          }}
          maxWidth="xl"
        >
          <ItemForm
            item={selectedItem || undefined}
            onSubmit={handleItemSubmit}
            onCancel={() => {
              setIsItemModalOpen(false);
              setSelectedItem(null);
            }}
            onDelete={selectedItem ? handleItemDelete : undefined}
            isSubmitting={isSubmitting}
            categories={categories_list}
            units={units_list}
          />
        </Modal>

        {/* Adjustment Modal (T067) */}
        <Modal
          isOpen={isAdjustmentModalOpen}
          onClose={() => setIsAdjustmentModalOpen(false)}
          maxWidth="xl"
        >
          <AdjustmentForm
            items={items || []}
            onSubmit={handleAdjustmentSubmit}
            onCancel={() => setIsAdjustmentModalOpen(false)}
            isSubmitting={isSubmitting}
          />
        </Modal>

        {/* Delete Confirmation Dialog (T059) */}
        {showDeleteConfirm && selectedItem && (
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75" />
            <div className="flex min-h-screen items-center justify-center p-4">
              <div className="relative w-full max-w-md transform rounded-lg bg-white p-6 shadow-xl">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Conferma Eliminazione
                </h3>
                <p className="text-sm text-gray-600 mb-6">
                  Sei sicuro di voler eliminare l'articolo{" "}
                  <strong>{selectedItem.name}</strong>?
                  <br />
                  <br />
                  L'articolo può essere eliminato solo se:
                  <br />
                  - La giacenza è zero
                  <br />- Non ci sono movimenti negli ultimi 12 mesi
                </p>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowDeleteConfirm(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    Annulla
                  </button>
                  <button
                    type="button"
                    onClick={confirmDelete}
                    className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? "Eliminazione..." : "Elimina"}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
