import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { format } from "date-fns";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { DashboardLayout } from "../components/layout/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { ReportPayload, SavedReport, reportsService } from "../services/reports";
import { analyticsService, AnalyticsFilters, DateRangeOption } from "../services/analytics";

type FormState = {
  id: number | null;
  name: string;
  description: string;
  metrics: string[];
  dateRange: string;
  startDate: string;
  endDate: string;
  source: string;
  repId: string;
  status: string;
  reportType: string;
  schedule: string;
};

const DEFAULT_FORM: FormState = {
  id: null,
  name: "",
  description: "",
  metrics: [],
  dateRange: "30days",
  startDate: "",
  endDate: "",
  source: "all",
  repId: "all",
  status: "all",
  reportType: "custom",
  schedule: "manual",
};

const METRIC_OPTIONS = [
  { value: "total_leads", label: "Total Leads" },
  { value: "conversion_rate", label: "Conversion Rate" },
  { value: "lead_sources_breakdown", label: "Lead Sources Breakdown" },
  { value: "score_distribution", label: "Score Distribution" },
  { value: "rep_performance", label: "Rep Performance" },
  { value: "timeline_analysis", label: "Timeline Analysis" },
  { value: "hot_leads", label: "Hot Leads" },
  { value: "avg_score", label: "Average Score" },
  { value: "conversion_funnel", label: "Conversion Funnel" },
];

const SCHEDULE_OPTIONS = [
  { value: "manual", label: "Manual (on-demand)" },
  { value: "daily", label: "Daily" },
  { value: "weekly", label: "Weekly" },
  { value: "monthly", label: "Monthly" },
];

const STATUS_OPTIONS = [
  { value: "all", label: "All statuses" },
  { value: "new", label: "New" },
  { value: "contacted", label: "Contacted" },
  { value: "qualified", label: "Qualified" },
  { value: "proposal", label: "Proposal" },
  { value: "negotiation", label: "Negotiation" },
  { value: "won", label: "Won" },
  { value: "lost", label: "Lost" },
];

function buildFiltersFromForm(form: FormState) {
  const filters: Record<string, any> = {
    date_range: form.dateRange,
  };

  if (form.dateRange === "custom") {
    if (form.startDate) filters.start_date = form.startDate;
    if (form.endDate) filters.end_date = form.endDate;
  }

  if (form.source !== "all") filters.source = form.source;
  if (form.repId !== "all") filters.rep_id = form.repId;
  if (form.status !== "all") filters.status = form.status;

  return filters;
}

function buildAnalyticsFilters(form: FormState): AnalyticsFilters & { status?: string } {
  return {
    dateRange: form.dateRange as DateRangeOption,
    startDate: form.dateRange === "custom" && form.startDate ? form.startDate : undefined,
    endDate: form.dateRange === "custom" && form.endDate ? form.endDate : undefined,
    source: form.source !== "all" ? form.source : undefined,
    repId: form.repId !== "all" ? form.repId : undefined,
    status: form.status !== "all" ? form.status : undefined,
  };
}

function parseFormFromReport(report: SavedReport): FormState {
  const filters = report.filters || {};
  return {
    id: report.id,
    name: report.name,
    description: report.description ?? "",
    metrics: report.metrics ?? [],
    dateRange: filters.date_range ?? "30days",
    startDate: filters.start_date ?? "",
    endDate: filters.end_date ?? "",
    source: filters.source ?? "all",
    repId: filters.rep_id ?? "all",
    status: filters.status ?? "all",
    reportType: report.report_type ?? "custom",
    schedule: report.schedule ?? "manual",
  };
}

function SectionHeading({ title }: { title: string }) {
  return <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">{title}</h3>;
}

export function ReportBuilder() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState<FormState>(DEFAULT_FORM);
  const [previewData, setPreviewData] = useState<Record<string, any>>({});
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [selectedReport, setSelectedReport] = useState<number | null>(null);
  const debounceRef = useRef<NodeJS.Timeout | null>(null);

  const savedReportsQuery = useQuery<SavedReport[]>({
    queryKey: ["reports"],
    queryFn: reportsService.listReports,
  });

  const leadSourcesQuery = useQuery<
    Array<{ source: string; count: number; converted: number; conversion_rate: number }>
  >({
    queryKey: ["report-builder-sources"],
    queryFn: async () => {
      const data = await analyticsService.getLeadSources({
        dateRange: "30days",
        source: undefined,
        repId: undefined,
      });
      return data.sources ?? [];
    },
  });

  const repsQuery = useQuery<
    Array<{ rep_id: string; rep_name: string; leads_assigned: number; conversion_rate: number }>
  >({
    queryKey: ["report-builder-reps"],
    queryFn: async () => {
      const data = await analyticsService.getRepPerformance({
        dateRange: "30days",
        source: undefined,
        repId: undefined,
      });
      return data.reps ?? [];
    },
  });

  const createMutation = useMutation<SavedReport, Error, ReportPayload>({
    mutationFn: reportsService.createReport,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      setForm(DEFAULT_FORM);
      setSelectedReport(null);
    },
  });

  const updateMutation = useMutation<SavedReport, Error, { id: number; data: Partial<ReportPayload> }>({
    mutationFn: (payload) =>
      reportsService.updateReport(payload.id, payload.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: reportsService.deleteReport,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      if (selectedReport !== null) {
        setForm(DEFAULT_FORM);
        setSelectedReport(null);
      }
    },
  });

  const runMutation = useMutation({
    mutationFn: (id: number) => reportsService.runReport(id),
    onSuccess: (data) => {
      setPreviewData(data.data);
    },
  });

  const handleMetricToggle = (metric: string) => {
    setForm((prev) => {
      const exists = prev.metrics.includes(metric);
      return {
        ...prev,
        metrics: exists ? prev.metrics.filter((m) => m !== metric) : [...prev.metrics, metric],
      };
    });
  };

  const handleChange = (field: keyof FormState, value: string) => {
    setForm((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSubmit = () => {
    if (!form.name || form.metrics.length === 0) {
      alert("Please provide a report name and select at least one metric.");
      return;
    }

    const payload = {
      name: form.name,
      description: form.description,
      report_type: form.reportType,
      filters: buildFiltersFromForm(form),
      metrics: form.metrics,
      schedule: form.schedule === "manual" ? null : form.schedule,
    };

    if (form.id) {
      updateMutation.mutate({ id: form.id, data: payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  const handleExport = (report: SavedReport, format: "csv" | "pdf" | "xlsx") => {
    reportsService.exportReport(report.id, format).then((response) => {
      const disposition = response.headers["content-disposition"];
      const filename =
        disposition?.split("filename=")?.[1]?.replace(/"/g, "") ?? `${report.name}.${format}`;
      const blob = new Blob([response.data], { type: response.headers["content-type"] });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    });
  };

  const handleEdit = (report: SavedReport) => {
    setSelectedReport(report.id);
    setForm(parseFormFromReport(report));
  };

  const handleReset = () => {
    setForm(DEFAULT_FORM);
    setSelectedReport(null);
  };

  const fetchPreview = useCallback(async () => {
    if (form.metrics.length === 0) {
      setPreviewData({});
      return;
    }
    setIsPreviewLoading(true);
    setPreviewError(null);
    try {
      const filters = buildAnalyticsFilters(form);
      const preview: Record<string, any> = {};

      const promises: Promise<void>[] = [];

      if (
        form.metrics.includes("total_leads") ||
        form.metrics.includes("conversion_rate") ||
        form.metrics.includes("hot_leads") ||
        form.metrics.includes("avg_score")
      ) {
        promises.push(
          analyticsService.getOverview(filters).then((data) => {
            preview.overview = data;
          }),
        );
      }

      if (form.metrics.includes("lead_sources_breakdown")) {
        promises.push(
          analyticsService.getLeadSources(filters).then((data) => {
            preview.lead_sources = data;
          }),
        );
      }

      if (form.metrics.includes("rep_performance")) {
        promises.push(
          analyticsService.getRepPerformance(filters).then((data) => {
            preview.rep_performance = data;
          }),
        );
      }

      if (form.metrics.includes("score_distribution")) {
        promises.push(
          analyticsService.getScoreDistribution(filters).then((data) => {
            preview.score_distribution = data;
          }),
        );
      }

      if (form.metrics.includes("timeline_analysis")) {
        promises.push(
          analyticsService.getTimeline(filters).then((data) => {
            preview.timeline = data;
          }),
        );
      }

      if (form.metrics.includes("conversion_funnel") || form.metrics.includes("conversion_rate")) {
        promises.push(
          analyticsService.getConversionFunnel(filters).then((data) => {
            preview.conversion_funnel = data;
          }),
        );
      }

      await Promise.all(promises);
      setPreviewData(preview);
    } catch (error: any) {
      console.error(error);
      setPreviewError(error?.userMessage || error?.message || "Failed to load preview.");
    } finally {
      setIsPreviewLoading(false);
    }
  }, [form]);

  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }
    debounceRef.current = setTimeout(() => {
      fetchPreview();
    }, 600);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [fetchPreview]);

  const savedReports = savedReportsQuery.data ?? [];
  const isEditing = form.id !== null;

  return (
    <DashboardLayout
      title="Custom Reports"
      subtitle="Save reusable analytics views, automate delivery, and export insights."
      actions={
        <Button onClick={handleSubmit} disabled={createMutation.isPending || updateMutation.isPending}>
          {isEditing ? "Update Report" : "Save Report"}
        </Button>
      }
    >
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>{isEditing ? "Edit Report Configuration" : "Create New Report"}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <SectionHeading title="Report Details" />
                  <label className="mt-2 block text-sm font-medium text-slate-700">Report Name</label>
                  <Input
                    className="mt-1"
                    value={form.name}
                    onChange={(event) => handleChange("name", event.target.value)}
                    placeholder="Executive summary"
                  />
                  <label className="mt-3 block text-sm font-medium text-slate-700">Description</label>
                  <Input
                    className="mt-1"
                    value={form.description}
                    onChange={(event) => handleChange("description", event.target.value)}
                    placeholder="Optional context for this report"
                  />
                </div>
                <div>
                  <SectionHeading title="Schedule" />
                  <label className="mt-2 block text-sm font-medium text-slate-700">Delivery cadence</label>
                  <Select value={form.schedule} onValueChange={(value) => handleChange("schedule", value)}>
                    <SelectTrigger className="mt-1">
                      <SelectValue placeholder="Manual" />
                    </SelectTrigger>
                    <SelectContent>
                      {SCHEDULE_OPTIONS.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <label className="mt-3 block text-sm font-medium text-slate-700">Report Type</label>
                  <Select value={form.reportType} onValueChange={(value) => handleChange("reportType", value)}>
                    <SelectTrigger className="mt-1">
                      <SelectValue placeholder="Custom" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="custom">Custom Report</SelectItem>
                      <SelectItem value="conversion">Conversion Insights</SelectItem>
                      <SelectItem value="source_analysis">Source Analysis</SelectItem>
                      <SelectItem value="rep_performance">Rep Performance</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <SectionHeading title="Metrics" />
                <div className="mt-3 grid grid-cols-1 gap-2 md:grid-cols-2 lg:grid-cols-3">
                  {METRIC_OPTIONS.map((metric) => {
                    const checked = form.metrics.includes(metric.value);
                    return (
                      <label
                        key={metric.value}
                        className={`flex cursor-pointer items-center gap-2 rounded-lg border px-3 py-2 text-sm transition ${
                          checked ? "border-navy-500 bg-navy-50 text-navy-700" : "border-slate-200 hover:border-navy-200"
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={() => handleMetricToggle(metric.value)}
                          className="h-4 w-4"
                        />
                        <span>{metric.label}</span>
                      </label>
                    );
                  })}
                </div>
              </div>

              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <SectionHeading title="Date Range" />
                  <label className="mt-2 block text-sm font-medium text-slate-700">Preset</label>
                  <Select value={form.dateRange} onValueChange={(value) => handleChange("dateRange", value)}>
                    <SelectTrigger className="mt-1">
                      <SelectValue placeholder="Last 30 days" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="7days">Last 7 days</SelectItem>
                      <SelectItem value="30days">Last 30 days</SelectItem>
                      <SelectItem value="90days">Last 90 days</SelectItem>
                      <SelectItem value="custom">Custom range</SelectItem>
                    </SelectContent>
                  </Select>
                  {form.dateRange === "custom" && (
                    <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
                      <div>
                        <label className="block text-sm font-medium text-slate-700">Start</label>
                        <Input
                          className="mt-1"
                          type="date"
                          value={form.startDate}
                          onChange={(event) => handleChange("startDate", event.target.value)}
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-700">End</label>
                        <Input
                          className="mt-1"
                          type="date"
                          value={form.endDate}
                          onChange={(event) => handleChange("endDate", event.target.value)}
                        />
                      </div>
                    </div>
                  )}
                </div>
                <div>
                  <SectionHeading title="Filters" />
                  <label className="mt-2 block text-sm font-medium text-slate-700">Lead Source</label>
                  <Select value={form.source} onValueChange={(value) => handleChange("source", value)}>
                    <SelectTrigger className="mt-1">
                      <SelectValue placeholder="All sources" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All sources</SelectItem>
                      {leadSourcesQuery.data?.map((source) => (
                        <SelectItem key={source.source} value={source.source}>
                          {source.source}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  <label className="mt-3 block text-sm font-medium text-slate-700">Sales Rep</label>
                  <Select value={form.repId} onValueChange={(value) => handleChange("repId", value)}>
                    <SelectTrigger className="mt-1">
                      <SelectValue placeholder="All reps" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All reps</SelectItem>
                      {repsQuery.data?.map((rep) => (
                        <SelectItem key={rep.rep_id} value={rep.rep_id}>
                          {rep.rep_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  <label className="mt-3 block text-sm font-medium text-slate-700">Status</label>
                  <Select value={form.status} onValueChange={(value) => handleChange("status", value)}>
                    <SelectTrigger className="mt-1">
                      <SelectValue placeholder="All statuses" />
                    </SelectTrigger>
                    <SelectContent>
                      {STATUS_OPTIONS.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="text-sm text-slate-500">
                  Reports are saved for your account. Scheduled reports will deliver via email when SMTP is configured.
                </div>
                <Button variant="outline" onClick={handleReset} type="button">
                  Reset
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
              <CardTitle>Preview</CardTitle>
              {previewError && <span className="text-sm text-red-600">{previewError}</span>}
            </CardHeader>
            <CardContent>
              {isPreviewLoading ? (
                <div className="flex h-40 items-center justify-center text-sm text-slate-500">Loading preview…</div>
              ) : Object.keys(previewData).length === 0 ? (
                <div className="flex h-40 items-center justify-center text-sm text-slate-500">
                  Select metrics to see a live preview.
                </div>
              ) : (
                <div className="space-y-6">
                  {previewData.overview && (
                    <div>
                      <h4 className="text-sm font-semibold text-slate-700">Overview</h4>
                      <div className="mt-2 grid grid-cols-2 gap-3 sm:grid-cols-4">
                        <div className="rounded-lg border border-slate-200 bg-white p-3 text-center">
                          <p className="text-xs uppercase tracking-wide text-slate-500">Total Leads</p>
                          <p className="mt-1 text-lg font-semibold text-slate-900">
                            {previewData.overview.total_leads ?? 0}
                          </p>
                        </div>
                        <div className="rounded-lg border border-slate-200 bg-white p-3 text-center">
                          <p className="text-xs uppercase tracking-wide text-slate-500">Conversion Rate</p>
                          <p className="mt-1 text-lg font-semibold text-slate-900">
                            {(previewData.overview.conversion_rate ?? 0).toFixed(1)}%
                          </p>
                        </div>
                        <div className="rounded-lg border border-slate-200 bg-white p-3 text-center">
                          <p className="text-xs uppercase tracking-wide text-slate-500">Hot Leads</p>
                          <p className="mt-1 text-lg font-semibold text-red-600">
                            {previewData.overview.hot_leads ?? 0}
                          </p>
                        </div>
                        <div className="rounded-lg border border-slate-200 bg-white p-3 text-center">
                          <p className="text-xs uppercase tracking-wide text-slate-500">Average Score</p>
                          <p className="mt-1 text-lg font-semibold text-navy-600">
                            {(previewData.overview.avg_score ?? 0).toFixed(1)}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {previewData.lead_sources && (
                    <div>
                      <h4 className="text-sm font-semibold text-slate-700">Lead Sources</h4>
                      <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
                        {previewData.lead_sources.sources?.map((source: any) => (
                          <div key={source.source} className="rounded-lg border border-slate-200 bg-white p-3">
                            <p className="text-sm font-semibold text-slate-800">{source.source}</p>
                            <p className="text-xs text-slate-500">
                              Leads: {source.count} • Converted: {source.converted} • Conversion:{" "}
                              {source.conversion_rate?.toFixed(1)}%
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {previewData.rep_performance && (
                    <div>
                      <h4 className="text-sm font-semibold text-slate-700">Rep Performance</h4>
                      <div className="mt-2 space-y-2">
                        {previewData.rep_performance.reps?.map((rep: any) => (
                          <div key={rep.rep_id} className="rounded-lg border border-slate-200 bg-white p-3">
                            <p className="text-sm font-semibold text-slate-800">{rep.rep_name}</p>
                            <p className="text-xs text-slate-500">
                              Leads: {rep.leads_assigned} • Contacted: {rep.leads_contacted} • Converted:{" "}
                              {rep.leads_converted} • Conversion: {rep.conversion_rate?.toFixed(1)}%
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Saved Reports</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {savedReportsQuery.isLoading ? (
                <div className="text-sm text-slate-500">Loading reports…</div>
              ) : savedReports.length === 0 ? (
                <div className="text-sm text-slate-500">
                  No saved reports yet. Configure a report and click “Save Report” to reuse it later.
                </div>
              ) : (
                savedReports.map((report) => (
                  <div
                    key={report.id}
                    className={`rounded-lg border p-3 transition ${
                      selectedReport === report.id ? "border-navy-500 bg-navy-50" : "border-slate-200 bg-white"
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm font-semibold text-slate-900">{report.name}</p>
                        <p className="text-xs text-slate-500">
                          {report.schedule ? `Scheduled: ${report.schedule}` : "Manual"}
                        </p>
                        <p className="mt-1 text-xs text-slate-400">
                          Last run:{" "}
                          {report.last_run ? format(new Date(report.last_run), "MMM d, yyyy HH:mm") : "Never"}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline" onClick={() => runMutation.mutate(report.id)}>
                          Run
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => handleEdit(report)}>
                          Edit
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            reportsService.exportReport(report.id, "pdf").then((response) => {
                              const disposition = response.headers["content-disposition"];
                              const filename =
                                disposition?.split("filename=")?.[1]?.replace(/"/g, "") ?? `${report.name}.pdf`;
                              const url = window.URL.createObjectURL(new Blob([response.data], { type: response.headers["content-type"] }));
                              const link = document.createElement("a");
                              link.href = url;
                              link.setAttribute("download", filename);
                              document.body.appendChild(link);
                              link.click();
                              document.body.removeChild(link);
                              window.URL.revokeObjectURL(url);
                            });
                          }}
                        >
                          PDF
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            reportsService.exportReport(report.id, "csv").then((response) => {
                              const disposition = response.headers["content-disposition"];
                              const filename =
                                disposition?.split("filename=")?.[1]?.replace(/"/g, "") ?? `${report.name}.csv`;
                              const url = window.URL.createObjectURL(new Blob([response.data], { type: response.headers["content-type"] }));
                              const link = document.createElement("a");
                              link.href = url;
                              link.setAttribute("download", filename);
                              document.body.appendChild(link);
                              link.click();
                              document.body.removeChild(link);
                              window.URL.revokeObjectURL(url);
                            });
                          }}
                        >
                          CSV
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            reportsService.exportReport(report.id, "xlsx").then((response) => {
                              const disposition = response.headers["content-disposition"];
                              const filename =
                                disposition?.split("filename=")?.[1]?.replace(/"/g, "") ?? `${report.name}.xlsx`;
                              const url = window.URL.createObjectURL(new Blob([response.data], { type: response.headers["content-type"] }));
                              const link = document.createElement("a");
                              link.href = url;
                              link.setAttribute("download", filename);
                              document.body.appendChild(link);
                              link.click();
                              document.body.removeChild(link);
                              window.URL.revokeObjectURL(url);
                            });
                          }}
                        >
                          Excel
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-red-600 hover:text-red-700"
                          onClick={() => deleteMutation.mutate(report.id)}
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}


