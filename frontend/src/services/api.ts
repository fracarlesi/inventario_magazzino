/**
 * API client for backend communication.
 * Uses fetch API with error handling and Italian error messages.
 */

import type { ItemWithStock, DashboardStats, ErrorResponse, ItemsQueryParams } from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

/**
 * Custom error class for API errors with Italian messages
 */
export class ApiError extends Error {
  constructor(
    public statusCode: number,
    public errorCode?: string,
    public context?: Record<string, any>
  ) {
    super();
  }
}

/**
 * Handle API response and extract error information
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorData: ErrorResponse | null = null;

    try {
      errorData = await response.json();
    } catch {
      // If JSON parsing fails, use generic error
      throw new ApiError(
        response.status,
        "UNKNOWN_ERROR",
        { message: "Errore di comunicazione con il server" }
      );
    }

    // Throw ApiError with Italian message from backend
    throw new ApiError(
      response.status,
      errorData.error_code,
      errorData.context
    );
  }

  return response.json();
}

/**
 * Build URL with query parameters
 */
function buildUrl(endpoint: string, params?: Record<string, any>): string {
  const url = new URL(`${API_BASE_URL}${endpoint}`);

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.append(key, String(value));
      }
    });
  }

  return url.toString();
}

/**
 * Fetch items with optional filters (FR-001, FR-002, FR-003, FR-004)
 */
export async function fetchItems(params?: ItemsQueryParams): Promise<ItemWithStock[]> {
  const url = buildUrl("/items", params);
  const response = await fetch(url);
  return handleResponse<ItemWithStock[]>(response);
}

/**
 * Fetch dashboard statistics (FR-041, FR-042)
 */
export async function fetchDashboardStats(): Promise<DashboardStats> {
  const url = buildUrl("/dashboard/stats");
  const response = await fetch(url);
  return handleResponse<DashboardStats>(response);
}

/**
 * Get unique categories for autocomplete
 * (This will be implemented in Phase 6 - US4)
 */
export async function fetchCategories(search?: string): Promise<string[]> {
  const url = buildUrl("/items/autocomplete/categories", { q: search });
  const response = await fetch(url);
  const data = await handleResponse<{ categories: string[] }>(response);
  return data.categories;
}

/**
 * Create a movement (IN/OUT/ADJUSTMENT)
 */
export async function createMovement(data: {
  item_id: string;
  quantity: string;
  movement_date: string;
  unit_cost_override?: string;
  note?: string;
  confirmed?: boolean;
  target_stock?: string;
}): Promise<any> {
  const url = `${API_BASE_URL}/movements`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return handleResponse(response);
}

/**
 * Create a new item (FR-013)
 */
export async function createItem(data: {
  name: string;
  category?: string;
  unit: string;
  notes?: string;
  min_stock: string;
  unit_cost: string;
}): Promise<ItemWithStock> {
  const url = `${API_BASE_URL}/items`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return handleResponse<ItemWithStock>(response);
}

/**
 * Update an existing item (FR-014)
 */
export async function updateItem(
  itemId: string,
  data: {
    name?: string;
    category?: string;
    unit?: string;
    notes?: string;
    min_stock?: string;
    unit_cost?: string;
  }
): Promise<ItemWithStock> {
  const url = `${API_BASE_URL}/items/${itemId}`;
  const response = await fetch(url, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return handleResponse<ItemWithStock>(response);
}

/**
 * Delete an item (FR-015, FR-016, FR-017)
 */
export async function deleteItem(itemId: string): Promise<void> {
  const url = `${API_BASE_URL}/items/${itemId}`;
  const response = await fetch(url, {
    method: "DELETE",
  });

  if (response.status === 204) {
    return; // Success, no content
  }

  return handleResponse<void>(response);
}

/**
 * Fetch movements with filters (FR-022, FR-023, FR-024)
 */
export async function fetchMovements(params?: {
  from_date?: string;
  to_date?: string;
  item_id?: string;
  movement_type?: string;
  limit?: number;
  offset?: number;
}): Promise<{ movements: any[]; total: number; limit: number; offset: number }> {
  const url = buildUrl("/movements", params);
  const response = await fetch(url);
  return handleResponse(response);
}

/**
 * Fetch export data for Excel generation (FR-025, FR-026, FR-027, FR-028)
 * Returns inventory and last 12 months movements
 */
export async function fetchExportData(): Promise<{
  export_date: string;
  period_start: string;
  period_end: string;
  inventory: ItemWithStock[];
  movements: any[];
}> {
  const url = `${API_BASE_URL}/export/preview`;
  const response = await fetch(url);
  return handleResponse(response);
}
