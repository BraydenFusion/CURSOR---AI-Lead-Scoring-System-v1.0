import { Fragment, useMemo, useState } from "react";
import { Dialog, Transition } from "@headlessui/react";
import { useMutation } from "@tanstack/react-query";
import { Download, Loader2, Upload, FileSpreadsheet, FileDown } from "lucide-react";

import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import {
  downloadTemplate,
  exportLeads,
  ExportFilters,
  ImportSummary,
  uploadCsv,
  uploadExcel,
} from "../services/importExport";
import DashboardLayout from "../components/layout/DashboardLayout";

type ImportFormat = "csv" | "excel";

const REQUIRED_COLUMNS = ["name", "email", "phone", "company", "location", "source"];

export default function ImportExportPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [detectedFormat, setDetectedFormat] = useState<ImportFormat | null>(null);
  const [previewHeaders, setPreviewHeaders] = useState<string[]>([]);
  const [importSummary, setImportSummary] = useState<ImportSummary | null>(null);
  const [showSummary, setShowSummary] = useState(false);
  const [importProgress, setImportProgress] = useState<number>(0);
  const [filters, setFilters] = useState<ExportFilters>({
    classification: "all",
    status: "all",
    fields: ["basic", "contact", "score"],
  });
  const [exportFormat, setExportFormat] = useState<"csv" | "excel">("csv");
  const [isDownloadingTemplate, setIsDownloadingTemplate] = useState(false);

  const importMutation = useMutation({
    mutationFn: async () => {
      if (!selectedFile || !detectedFormat) {
        throw new Error("Select a file before importing.");
      }
      setImportProgress(35);
      const summary =
        detectedFormat === "csv" ? await uploadCsv(selectedFile) : await uploadExcel(selectedFile);
      return summary;
    },
    onSuccess: (summary) => {
      setImportProgress(100);
      setImportSummary(summary);
      setShowSummary(true);
    },
    onError: (error: unknown) => {
      setImportProgress(0);
      const message = error instanceof Error ? error.message : "Import failed. Please try again.";
      setImportSummary({
        total_rows: 0,
        success_count: 0,
        error_count: 1,
        errors: [{ row: 0, error: message }],
      });
      setShowSummary(true);
    },
  });

  const exportMutation = useMutation({
    mutationFn: async () => {
      const blob = await exportLeads(exportFormat, filters);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = exportFormat === "csv" ? "leads_export.csv" : "leads_export.xlsx";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    },
  });

  const handleFileSelection = async (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) {
      setSelectedFile(null);
      setDetectedFormat(null);
      setPreviewHeaders([]);
      return;
    }

    const file = fileList[0];
    const extension = file.name.toLowerCase().split(".").pop();
    if (!extension || !["csv", "xlsx", "xls"].includes(extension)) {
      alert("Unsupported file type. Please upload a CSV or Excel file.");
      return;
    }

    const format: ImportFormat = extension === "csv" ? "csv" : "excel";
    setSelectedFile(file);
    setDetectedFormat(format);
    setImportProgress(0);
    setImportSummary(null);

    if (format === "csv") {
      const text = await file.text();
      const [firstLine] = text.split(/\r?\n/);
      if (firstLine) {
        const headers = firstLine.split(",").map((col) => col.trim());
        setPreviewHeaders(headers.filter((header) => header));
      }
    } else {
      setPreviewHeaders(REQUIRED_COLUMNS);
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      setIsDownloadingTemplate(true);
      const blob = await downloadTemplate();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "lead_import_template.xlsx";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } finally {
      setIsDownloadingTemplate(false);
    }
  };

  const handleImport = () => {
    if (!selectedFile || !detectedFormat) {
      alert("Select a CSV or Excel file to import.");
      return;
    }
    setImportProgress(10);
    importMutation.mutate();
  };

  const handleFilterChange = (event: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
    const { name, value, type, checked } = event.target;
    if (type === "checkbox") {
      setFilters((prev) => {
        const fields = new Set(prev.fields ?? []);
        if (checked) {
          fields.add(value);
        } else {
          fields.delete(value);
        }
        return { ...prev, fields: Array.from(fields) };
      });
    } else {
      setFilters((prev) => ({
        ...prev,
        [name]: value === "" ? undefined : value,
      }));
    }
  };

  const downloadErrors = () => {
    if (!importSummary || importSummary.errors.length === 0) {
      return;
    }
    const header = "row,error\n";
    const lines = importSummary.errors.map((item) => `${item.row},"${item.error.replace(/"/g, '""')}"`);
    const csv = `${header}${lines.join("\n")}`;
    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "import_errors.csv";
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  };

  const progressLabel = useMemo(() => {
    if (importProgress === 0) return "Waiting to start";
    if (importProgress < 35) return "Preparing import…";
    if (importProgress < 100) return "Processing rows…";
    return "Import complete!";
  }, [importProgress]);

  return (
    <DashboardLayout
      title="Lead Import & Export"
      subtitle="Upload large lead lists or export enriched data for downstream workflows."
    >
      <div className="space-y-8">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between gap-4">
              <div>
                <CardTitle>Import Leads</CardTitle>
                <CardDescription>Upload CSV or Excel files (up to 10,000 rows).</CardDescription>
              </div>
              <Button variant="outline" onClick={handleDownloadTemplate} disabled={isDownloadingTemplate}>
                {isDownloadingTemplate ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Preparing…
                  </>
                ) : (
                  <>
                    <Download className="mr-2 h-4 w-4" />
                    Download Template
                  </>
                )}
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <label
              onDragOver={(event) => event.preventDefault()}
              onDrop={(event) => {
                event.preventDefault();
                handleFileSelection(event.dataTransfer.files);
              }}
              className="flex w-full cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-slate-300 bg-slate-50 px-6 py-10 text-center transition hover:border-slate-400 hover:bg-slate-100"
            >
              <Upload className="mb-3 h-8 w-8 text-slate-500" />
              <p className="text-sm font-medium text-slate-700">
                Drag and drop a CSV or Excel file, or click to browse
              </p>
              <p className="text-xs text-slate-500 mt-1">Max file size: 20 MB</p>
              <Input
                type="file"
                accept=".csv,.xlsx,.xls"
                className="hidden"
                onChange={(event) => handleFileSelection(event.target.files)}
              />
            </label>

            {selectedFile && (
              <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold text-slate-800">{selectedFile.name}</p>
                    <p className="text-xs text-slate-500">
                      {(selectedFile.size / 1024).toFixed(1)} KB •{" "}
                      {detectedFormat?.toUpperCase()} detected
                    </p>
                  </div>
                  <Button variant="ghost" onClick={() => handleFileSelection(null)}>
                    Remove
                  </Button>
                </div>
                <div className="mt-4">
                  <h4 className="text-sm font-semibold text-slate-700">Field Mapping Preview</h4>
                  <p className="text-xs text-slate-500">
                    Required columns: {REQUIRED_COLUMNS.join(", ")}
                  </p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {previewHeaders.length > 0 ? (
                      previewHeaders.map((header) => (
                        <span
                          key={header}
                          className="rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs text-slate-700"
                        >
                          {header}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-slate-500">
                        Column preview unavailable for this format.
                      </span>
                    )}
                  </div>
                </div>
              </div>
            )}

            {importProgress > 0 && (
              <div>
                <div className="mb-1 flex items-center justify-between text-xs text-slate-500">
                  <span>{progressLabel}</span>
                  <span>{importProgress}%</span>
                </div>
                <div className="h-2 w-full rounded-full bg-slate-200">
                  <div
                    className="h-2 rounded-full bg-indigo-500 transition-all"
                    style={{ width: `${importProgress}%` }}
                  />
                </div>
              </div>
            )}

            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={handleDownloadTemplate}>
                <FileSpreadsheet className="mr-2 h-4 w-4" />
                Template
              </Button>
              <Button onClick={handleImport} disabled={!selectedFile || importMutation.isLoading}>
                {importMutation.isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Importing…
                  </>
                ) : (
                  <>
                    <Upload className="mr-2 h-4 w-4" />
                    Import Leads
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Export Leads</CardTitle>
            <CardDescription>
              Download enriched lead data with scoring breakdown, activities, and notes.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Lead Classification</label>
                <select
                  name="classification"
                  value={filters.classification ?? "all"}
                  onChange={handleFilterChange}
                  className="w-full rounded-md border px-3 py-2 text-sm"
                >
                  <option value="all">All classifications</option>
                  <option value="hot">Hot</option>
                  <option value="warm">Warm</option>
                  <option value="cold">Cold</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Lead Status</label>
                <select
                  name="status"
                  value={filters.status ?? "all"}
                  onChange={handleFilterChange}
                  className="w-full rounded-md border px-3 py-2 text-sm"
                >
                  <option value="all">All statuses</option>
                  <option value="new">New</option>
                  <option value="contacted">Contacted</option>
                  <option value="qualified">Qualified</option>
                  <option value="proposal">Proposal</option>
                  <option value="negotiation">Negotiation</option>
                  <option value="won">Won</option>
                  <option value="lost">Lost</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Source</label>
                <Input
                  name="source"
                  placeholder="e.g. Webinar"
                  value={filters.source ?? ""}
                  onChange={handleFilterChange}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Format</label>
                <select
                  value={exportFormat}
                  onChange={(event) => setExportFormat(event.target.value as "csv" | "excel")}
                  className="w-full rounded-md border px-3 py-2 text-sm"
                >
                  <option value="csv">CSV</option>
                  <option value="excel">Excel (multi-sheet)</option>
                </select>
              </div>
            </div>
            <div className="grid gap-3 md:grid-cols-3">
              {[
                { name: "basic", label: "Basic info" },
                { name: "contact", label: "Contact details" },
                { name: "score", label: "Scoring breakdown" },
                { name: "activities", label: "Activities" },
                { name: "notes", label: "Notes" },
                { name: "assignments", label: "Assignments" },
              ].map(({ name, label }) => (
                <label key={name} className="flex items-center gap-2 text-sm text-slate-700">
                  <input
                    type="checkbox"
                    value={name}
                    checked={filters.fields?.includes(name)}
                    onChange={handleFilterChange}
                    className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  {label}
                </label>
              ))}
            </div>

            <div className="flex justify-end">
              <Button onClick={() => exportMutation.mutate()} disabled={exportMutation.isLoading}>
                {exportMutation.isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Building export…
                  </>
                ) : (
                  <>
                    <FileDown className="mr-2 h-4 w-4" />
                    Export Leads
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <Transition appear show={showSummary} as={Fragment}>
        <Dialog as="div" className="relative z-50" onClose={() => setShowSummary(false)}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-200"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-150"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black/30" />
          </Transition.Child>
          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-200"
                enterFrom="opacity-0 scale-95"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-150"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-xl rounded-xl bg-white p-6 shadow-xl">
                  <Dialog.Title className="text-lg font-semibold text-slate-900">
                    Import Summary
                  </Dialog.Title>
                  <div className="mt-4 space-y-4 text-sm text-slate-700">
                    {importSummary ? (
                      <>
                        <p>Total rows processed: {importSummary.total_rows}</p>
                        <p className="text-emerald-600">
                          Successfully imported: {importSummary.success_count}
                        </p>
                        <p className="text-amber-600">
                          Failed rows: {importSummary.error_count}
                        </p>
                        {importSummary.errors.length > 0 && (
                          <div className="rounded-md border border-amber-200 bg-amber-50 p-3">
                            <p className="font-semibold text-amber-700">Row issues</p>
                            <ul className="mt-2 max-h-48 space-y-1 overflow-y-auto text-xs text-amber-700">
                              {importSummary.errors.slice(0, 10).map((error, index) => (
                                <li key={`${error.row}-${index}`}>
                                  Row {error.row}: {error.error}
                                </li>
                              ))}
                              {importSummary.errors.length > 10 && (
                                <li>…and {importSummary.errors.length - 10} more</li>
                              )}
                            </ul>
                            <Button
                              variant="outline"
                              size="sm"
                              className="mt-3"
                              onClick={downloadErrors}
                            >
                              Download error report
                            </Button>
                          </div>
                        )}
                      </>
                    ) : (
                      <p>Import completed.</p>
                    )}
                  </div>
                  <div className="mt-6 flex justify-end">
                    <Button onClick={() => setShowSummary(false)}>Close</Button>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
    </DashboardLayout>
  );
}

