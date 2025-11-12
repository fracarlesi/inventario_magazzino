/**
 * TypeScript types for API requests and responses.
 * These match the Pydantic schemas from backend/src/models/schemas.py
 */

export interface ItemWithStock {
  id: string; // UUID
  name: string;
  category: string | null;
  unit: string;
  notes: string | null;
  min_stock: string; // Decimal as string for precision
  unit_cost: string; // Decimal as string
  stock_quantity: string; // Decimal as string
  stock_value: string; // Decimal as string
  is_under_min_stock: boolean;
  last_movement_at: string | null; // ISO datetime
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
}

export interface DashboardStats {
  total_warehouse_value: string; // Decimal as string (EUR)
  under_stock_count: number;
  total_items_count: number;
  zero_stock_count: number;
}

export interface ErrorResponse {
  detail: string; // Human-readable Italian error message
  error_code?: string; // Machine-readable error code
  context?: Record<string, any>; // Additional error context
}

export interface ItemsQueryParams {
  search?: string;
  category?: string;
  under_stock_only?: boolean;
  sort_by?: "name" | "category" | "stock_quantity" | "is_under_min_stock";
  sort_order?: "asc" | "desc";
}
