"use client";

import translations from "@/i18n/it.json";

const t = translations.dashboard.filters.category;

interface CategoryFilterProps {
  categories: string[];
  selectedCategory: string | null;
  onCategoryChange: (category: string | null) => void;
}

export default function CategoryFilter({
  categories,
  selectedCategory,
  onCategoryChange,
}: CategoryFilterProps) {
  return (
    <div className="w-full max-w-xs">
      <label
        htmlFor="category-select"
        className="block text-sm font-medium text-gray-700 mb-1"
      >
        {t.label}
      </label>
      <select
        id="category-select"
        className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
        value={selectedCategory || ""}
        onChange={(e) =>
          onCategoryChange(e.target.value === "" ? null : e.target.value)
        }
      >
        <option value="">{t.all}</option>
        {categories.map((category) => (
          <option key={category} value={category}>
            {category}
          </option>
        ))}
      </select>
    </div>
  );
}
