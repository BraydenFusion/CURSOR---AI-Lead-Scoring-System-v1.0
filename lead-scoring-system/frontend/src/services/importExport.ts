import apiClient from "./api";

export type ImportSummary = {
  total_rows: number;
  success_count: number;
  error_count: number;
  errors: Array<{ row: number; error: string }>;
};

export async function uploadCsv(file: File): Promise<ImportSummary> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await apiClient.post<ImportSummary>("/import/csv", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function uploadExcel(file: File): Promise<ImportSummary> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await apiClient.post<ImportSummary>("/import/excel", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function downloadTemplate(): Promise<Blob> {
  const response = await apiClient.get<ArrayBuffer>("/import/template", {
    responseType: "arraybuffer",
  });
  return new Blob([response.data], {
    type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  });
}

export type ExportFilters = {
  classification?: string;
  status?: string;
  source?: string;
  created_from?: string;
  created_to?: string;
  fields?: string[];
};

export async function exportLeads(format: "csv" | "excel", filters: ExportFilters): Promise<Blob> {
  const endpoint = format === "csv" ? "/export/csv" : "/export/excel";
  const response = await apiClient.post<ArrayBuffer>(endpoint, filters, {
    responseType: "arraybuffer",
  });
  const type =
    format === "csv"
      ? "text/csv"
      : "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
  return new Blob([response.data], { type });
}

