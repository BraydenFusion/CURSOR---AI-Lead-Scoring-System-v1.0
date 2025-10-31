import { Search } from "lucide-react";

import { Input } from "./ui/input";
import { Label } from "./ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";

interface LeadFiltersProps {
  filters: {
    sort: "score" | "date" | "source";
    classification: "all" | "hot" | "warm" | "cold";
    search?: string;
  };
  onFilterChange: (filters: Partial<LeadFiltersProps["filters"]>) => void;
}

export function LeadFilters({ filters, onFilterChange }: LeadFiltersProps) {
  return (
    <div className="flex flex-col gap-4 rounded-lg border border-slate-200 bg-white p-4 shadow-sm lg:flex-row lg:items-end lg:justify-between">
      <div className="flex flex-1 flex-col gap-4 sm:flex-row">
        <div className="w-full sm:w-48">
          <Label className="mb-1 block text-slate-600">Classification</Label>
          <Select
            value={filters.classification}
            onValueChange={(value) =>
              onFilterChange({ classification: value as LeadFiltersProps["filters"]["classification"] })
            }
          >
            <SelectTrigger>
              <SelectValue placeholder="Classification" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Leads</SelectItem>
              <SelectItem value="hot">Hot</SelectItem>
              <SelectItem value="warm">Warm</SelectItem>
              <SelectItem value="cold">Cold</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="w-full sm:w-48">
          <Label className="mb-1 block text-slate-600">Sort By</Label>
          <Select
            value={filters.sort}
            onValueChange={(value) =>
              onFilterChange({ sort: value as LeadFiltersProps["filters"]["sort"] })
            }
          >
            <SelectTrigger>
              <SelectValue placeholder="Sort" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="score">Score (High -> Low)</SelectItem>
              <SelectItem value="date">Created Date</SelectItem>
              <SelectItem value="source">Lead Source</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <div className="relative w-full lg:max-w-sm">
        <Label className="mb-1 block text-slate-600">Search</Label>
        <Search className="absolute left-2 top-9 h-4 w-4 text-slate-400" />
        <Input
          className="pl-8"
          placeholder="Search by name or email"
          value={filters.search ?? ""}
          onChange={(event) => onFilterChange({ search: event.target.value })}
        />
      </div>
    </div>
  );
}
