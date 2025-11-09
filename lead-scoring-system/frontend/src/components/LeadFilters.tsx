import { useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { FileSpreadsheet } from "lucide-react";

export function LeadFilters() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col gap-3 rounded-lg border bg-white p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between">
      <div className="flex flex-1 flex-col gap-3 sm:flex-row">
        <select className="w-full min-h-[44px] rounded-md border px-3 py-2 text-base sm:w-40">
          <option value="all">All Leads</option>
          <option value="hot">Hot</option>
          <option value="warm">Warm</option>
          <option value="cold">Cold</option>
        </select>
        <select className="w-full min-h-[44px] rounded-md border px-3 py-2 text-base sm:w-40">
          <option value="score">Sort by Score</option>
          <option value="date">Sort by Date</option>
          <option value="source">Sort by Source</option>
        </select>
      </div>
      <input 
        className="w-full min-h-[44px] rounded-md border px-3 py-2 text-base sm:w-72"
        placeholder="Search leads" 
        type="text"
      />
      <div className="flex items-center justify-end sm:justify-start">
        <Button
          variant="outline"
          className="flex items-center gap-2"
          onClick={() => navigate("/leads/import-export")}
        >
          <FileSpreadsheet className="h-4 w-4" />
          Import / Export
        </Button>
      </div>
    </div>
  );
}
