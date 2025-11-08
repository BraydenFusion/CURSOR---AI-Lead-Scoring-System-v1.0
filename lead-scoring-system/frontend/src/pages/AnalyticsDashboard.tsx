import { useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  FunnelChart,
  Funnel,
  LabelList,
  LineChart,
  Line,
  Cell,
} from "recharts";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";

import { DashboardLayout } from "../components/layout/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { Input } from "../components/ui/input";
import { analyticsService, AnalyticsFilters, DateRangeOption } from "../services/analytics";

type OverviewResponse = {
  total_leads: number;
  hot_leads: number;
  warm_leads: number;
  cold_leads: number;
  conversion_rate: number;
  avg_score: number;
  leads_this_month: number;
  leads_last_month: number;
  growth_rate: number;
};

type FunnelStage = {
  name: string;
  count: number;
  percentage: number;
};

type FunnelResponse = {
  stages: FunnelStage[];
};

type LeadSourceRow = {
  source: string;
  count: number;
  converted: number;
  conversion_rate: number;
};

type LeadSourcesResponse = {
  sources: LeadSourceRow[];
};

type RepPerformanceRow = {
  rep_id: string;
  rep_name: string;
  leads_assigned: number;
  leads_contacted: number;
  leads_converted: number;
  conversion_rate: number;
  avg_response_time_hours: number;
};

type RepPerformanceResponse = {
  reps: RepPerformanceRow[];
};

type ScoreDistributionRow = {
  range: string;
  count: number;
};

type ScoreDistributionResponse = {
  distribution: ScoreDistributionRow[];
};

type TimelineRow = {
  date: string;
  new_leads: number;
  contacted: number;
  converted: number;
  avg_score: number;
};

type TimelineResponse = {
  period: string;
  daily_stats: TimelineRow[];
};

type KPI = {
  label: string;
  value: string;
  caption?: string;
  trend?: number;
  tone?: "default" | "success" | "warning";
};

const funnelColors = ["#0ea5e9", "#6366f1", "#f59e0b", "#10b981"];

function ChartSkeleton({ message = "Loading analytics..." }: { message?: string }) {
  return (
    <div className="flex h-64 items-center justify-center rounded-lg border border-dashed border-slate-200 bg-slate-50 text-sm text-slate-400">
      {message}
    </div>
  );
}

function ErrorState({ message = "Unable to load data." }: { message?: string }) {
  return (
    <div className="flex h-64 items-center justify-center rounded-lg border border-red-200 bg-red-50 text-sm text-red-600">
      {message}
    </div>
  );
}

export function AnalyticsDashboard() {
  const navigate = useNavigate();
  const reportRef = useRef<HTMLDivElement>(null);
  const [isExporting, setIsExporting] = useState(false);

  const [dateRange, setDateRange] = useState<DateRangeOption>("30days");
  const [customRange, setCustomRange] = useState<{ start: string | null; end: string | null }>({
    start: null,
    end: null,
  });
  const [source, setSource] = useState<string>("all");
  const [repId, setRepId] = useState<string>("all");

  const customStart = customRange.start;
  const customEnd = customRange.end;
  const hasValidCustomRange = dateRange !== "custom" || Boolean(customStart && customEnd);

  const analyticsFilters = useMemo<AnalyticsFilters>(
    () => ({
      dateRange,
      startDate: dateRange === "custom" ? customStart ?? undefined : undefined,
      endDate: dateRange === "custom" ? customEnd ?? undefined : undefined,
      source,
      repId,
    }),
    [dateRange, customStart, customEnd, source, repId],
  );

  const overviewQuery = useQuery<OverviewResponse, Error, OverviewResponse, readonly [string, AnalyticsFilters]>({
    queryKey: ["analytics-overview", analyticsFilters] as const,
    queryFn: () => analyticsService.getOverview(analyticsFilters),
    enabled: hasValidCustomRange,
  });

  const funnelQuery = useQuery<FunnelResponse, Error, FunnelResponse, readonly [string, AnalyticsFilters]>({
    queryKey: ["analytics-funnel", analyticsFilters] as const,
    queryFn: () => analyticsService.getConversionFunnel(analyticsFilters),
    enabled: hasValidCustomRange,
  });

  const leadSourcesQuery = useQuery<LeadSourcesResponse, Error, LeadSourcesResponse, readonly [string, AnalyticsFilters]>({
    queryKey: ["analytics-lead-sources", analyticsFilters] as const,
    queryFn: () => analyticsService.getLeadSources(analyticsFilters),
    enabled: hasValidCustomRange,
  });

  const repPerformanceQuery = useQuery<RepPerformanceResponse, Error, RepPerformanceResponse, readonly [string, AnalyticsFilters]>({
    queryKey: ["analytics-rep-performance", analyticsFilters] as const,
    queryFn: () => analyticsService.getRepPerformance(analyticsFilters),
    enabled: hasValidCustomRange,
  });

  const scoreDistributionQuery = useQuery<ScoreDistributionResponse, Error, ScoreDistributionResponse, readonly [string, AnalyticsFilters]>({
    queryKey: ["analytics-score-distribution", analyticsFilters] as const,
    queryFn: () => analyticsService.getScoreDistribution(analyticsFilters),
    enabled: hasValidCustomRange,
  });

  const timelineQuery = useQuery<TimelineResponse, Error, TimelineResponse, readonly [string, AnalyticsFilters]>({
    queryKey: ["analytics-timeline", analyticsFilters] as const,
    queryFn: () => analyticsService.getTimeline(analyticsFilters),
    enabled: hasValidCustomRange,
  });

  const sources = useMemo<LeadSourceRow[]>(
    () => leadSourcesQuery.data?.sources ?? [],
    [leadSourcesQuery.data?.sources],
  );

  const reps = useMemo<RepPerformanceRow[]>(
    () => repPerformanceQuery.data?.reps ?? [],
    [repPerformanceQuery.data?.reps],
  );

  const topKpis: KPI[] = useMemo(() => {
    if (!overviewQuery.data) return [];

    const { total_leads, growth_rate, conversion_rate, hot_leads, avg_score } = overviewQuery.data;
    const tone: KPI["tone"] =
      avg_score >= 75 ? "success" : avg_score >= 60 ? "warning" : "default";

    return [
      {
        label: "Total Leads",
        value: total_leads.toLocaleString(),
        caption: `MoM Growth ${growth_rate.toFixed(1)}%`,
        trend: growth_rate,
      },
      {
        label: "Conversion Rate",
        value: `${conversion_rate.toFixed(1)}%`,
        caption: conversion_rate >= 25 ? "Strong performance" : "Needs attention",
        trend: conversion_rate,
      },
      {
        label: "Hot Leads",
        value: hot_leads.toLocaleString(),
        caption: "Ready for immediate outreach",
      },
      {
        label: "Average Score",
        value: avg_score.toFixed(1),
        caption: "AI-calculated lead quality",
        tone,
      },
    ];
  }, [overviewQuery.data]);

  const scoreDistribution: ScoreDistributionRow[] =
    scoreDistributionQuery.data?.distribution ?? [];
  const funnelStages: FunnelStage[] = funnelQuery.data?.stages ?? [];
  const timelineStats: TimelineRow[] = timelineQuery.data?.daily_stats ?? [];

  const repOptions = useMemo(
    () =>
      reps.map((rep: RepPerformanceRow) => ({
      value: rep.rep_id,
      label: rep.rep_name,
      })),
    [reps],
  );

  const sourceOptions = useMemo(
    () =>
      sources.map((item: LeadSourceRow) => ({
      value: item.source,
      label: item.source,
      })),
    [sources],
  );

  const handleDateRangeChange = (value: DateRangeOption) => {
    setDateRange(value);
    if (value !== "custom") {
      setCustomRange({ start: null, end: null });
    }
  };

  const handleExportReport = async () => {
    if (!reportRef.current) return;
    try {
      setIsExporting(true);
      const canvas = await html2canvas(reportRef.current, {
        backgroundColor: "#ffffff",
        scale: window.devicePixelRatio > 1 ? 2 : 1.5,
        useCORS: true,
      });

      const imageData = canvas.toDataURL("image/png");
      const pdf = new jsPDF("p", "mm", "a4");
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();

      const imgProps = pdf.getImageProperties(imageData);
      const pdfHeight = (imgProps.height * pageWidth) / imgProps.width;

      let renderedHeight = 0;
      let position = 0;

      while (renderedHeight < pdfHeight) {
        pdf.addImage(imageData, "PNG", 0, position, pageWidth, pdfHeight);
        renderedHeight += pageHeight;
        if (renderedHeight < pdfHeight - 1) {
          pdf.addPage();
          position = -renderedHeight;
        }
      }

      pdf.save(`analytics-report-${format(new Date(), "yyyy-MM-dd")}.pdf`);
    } finally {
      setIsExporting(false);
    }
  };

  const handleExportRepCsv = () => {
    if (!reps.length) return;
    const rows = [
      ["Sales Rep", "Leads Assigned", "Leads Contacted", "Leads Converted", "Conversion Rate (%)", "Avg Response (hrs)"],
      ...reps.map((rep) => [
        rep.rep_name,
        rep.leads_assigned,
        rep.leads_contacted,
        rep.leads_converted,
        rep.conversion_rate,
        rep.avg_response_time_hours,
      ]),
    ];

    const csvContent = rows
      .map((row) =>
        row
          .map((value) =>
            typeof value === "string"
              ? `"${value.replace(/"/g, '""')}"`
              : `"${String(value)}"`,
          )
          .join(","),
      )
      .join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `rep-performance-${format(new Date(), "yyyy-MM-dd")}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  return (
    <DashboardLayout
      title="Analytics Intelligence"
      subtitle="Deep dive into pipeline health, conversion performance, and rep efficiency."
      actions={
        <Button onClick={handleExportReport} disabled={isExporting || !hasValidCustomRange}>
          {isExporting ? "Generating..." : "Export Report"}
        </Button>
      }
    >
      <div className="space-y-6" ref={reportRef}>
        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle>Filters</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
              <div>
                <label className="block text-sm font-medium text-slate-700">Date Range</label>
    <Select
      value={dateRange}
      onValueChange={(value) => handleDateRangeChange(value as DateRangeOption)}
    >
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Select range" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="7days">Last 7 days</SelectItem>
                    <SelectItem value="30days">Last 30 days</SelectItem>
                    <SelectItem value="90days">Last 90 days</SelectItem>
                    <SelectItem value="custom">Custom range</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {dateRange === "custom" && (
                <div className="flex flex-col gap-3 md:col-span-2 xl:col-span-1">
                  <div>
                    <label className="block text-sm font-medium text-slate-700">Start date</label>
                    <Input
                      type="date"
                      className="mt-1"
                      value={customStart ?? ""}
                      onChange={(event) => setCustomRange((prev) => ({ ...prev, start: event.target.value || null }))}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700">End date</label>
                    <Input
                      type="date"
                      className="mt-1"
                      value={customEnd ?? ""}
                      onChange={(event) => setCustomRange((prev) => ({ ...prev, end: event.target.value || null }))}
                    />
                  </div>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-slate-700">Lead Source</label>
                <Select value={source} onValueChange={setSource}>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="All sources" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All sources</SelectItem>
                    {sourceOptions.map((item) => (
                      <SelectItem key={item.value} value={item.value}>
                        {item.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700">Sales Rep</label>
                <Select value={repId} onValueChange={setRepId}>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="All reps" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All reps</SelectItem>
                    {repOptions.map((item) => (
                      <SelectItem key={item.value} value={item.value}>
                        {item.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {overviewQuery.isLoading && <ChartSkeleton message="Loading KPIs..." />}
          {overviewQuery.isError && <ErrorState message="Unable to load KPI summary." />}
          {!overviewQuery.isLoading &&
            !overviewQuery.isError &&
            topKpis.map((kpi) => (
              <Card
                key={kpi.label}
                className={
                  kpi.tone === "success"
                    ? "border-green-200 bg-green-50"
                    : kpi.tone === "warning"
                    ? "border-amber-200 bg-amber-50"
                    : ""
                }
              >
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-slate-600">{kpi.label}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-semibold text-slate-900">{kpi.value}</p>
                  {kpi.caption && <p className="mt-2 text-sm text-slate-500">{kpi.caption}</p>}
                </CardContent>
              </Card>
            ))}
        </div>

        {/* Lead Source Performance */}
        <Card>
          <CardHeader>
            <CardTitle>Lead Source Performance</CardTitle>
          </CardHeader>
          <CardContent>
            {leadSourcesQuery.isLoading && <ChartSkeleton />}
            {leadSourcesQuery.isError && <ErrorState message="Unable to load lead sources." />}
            {!leadSourcesQuery.isLoading && !leadSourcesQuery.isError && sources.length === 0 && (
              <ChartSkeleton message="No lead source data for the selected filters." />
            )}
            {!leadSourcesQuery.isLoading && !leadSourcesQuery.isError && sources.length > 0 && (
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={sources}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="source" />
                    <YAxis />
                    <Tooltip
                      formatter={(value: number, name) =>
                        name === "conversion_rate" ? [`${value.toFixed(1)}%`, "Conversion Rate"] : [value, name === "count" ? "Leads" : "Converted"]
                      }
                    />
                    <Legend />
                    <Bar dataKey="count" name="Total Leads" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="converted" name="Converted Leads" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Conversion Funnel & Score Distribution */}
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Conversion Funnel</CardTitle>
            </CardHeader>
            <CardContent>
              {funnelQuery.isLoading && <ChartSkeleton />}
              {funnelQuery.isError && <ErrorState message="Unable to load funnel data." />}
              {!funnelQuery.isLoading && !funnelQuery.isError && funnelStages.length === 0 && (
                <ChartSkeleton message="No funnel data for the selected filters." />
              )}
              {!funnelQuery.isLoading && !funnelQuery.isError && funnelStages.length > 0 && (
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <FunnelChart>
                      <Tooltip />
                      <Funnel dataKey="count" data={funnelStages} isAnimationActive>
                        <LabelList
                          position="right"
                          dataKey="percentage"
                          formatter={(value: any) => `${value}%`}
                        />
                        {funnelStages.map((stage: FunnelStage, index: number) => (
                          <Cell key={stage.name} fill={funnelColors[index] ?? "#64748b"} />
                        ))}
                      </Funnel>
                    </FunnelChart>
                  </ResponsiveContainer>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Score Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              {scoreDistributionQuery.isLoading && <ChartSkeleton />}
              {scoreDistributionQuery.isError && (
                <ErrorState message="Unable to load score distribution." />
              )}
              {!scoreDistributionQuery.isLoading &&
                !scoreDistributionQuery.isError &&
                scoreDistribution.length === 0 && (
                  <ChartSkeleton message="No score data for the selected filters." />
                )}
              {!scoreDistributionQuery.isLoading &&
                !scoreDistributionQuery.isError &&
                scoreDistribution.length > 0 && (
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={scoreDistribution}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis dataKey="range" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" name="Lead count" radius={[4, 4, 0, 0]}>
                          {scoreDistribution.map((entry: ScoreDistributionRow) => {
                            const rangeMax = parseInt(entry.range.split("-")[1], 10);
                            const fill =
                              rangeMax >= 81
                                ? "#ef4444"
                                : rangeMax >= 61
                                ? "#f59e0b"
                                : "#2563eb";
                            return <Cell key={entry.range} fill={fill} />;
                          })}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}
            </CardContent>
          </Card>
        </div>

        {/* Timeline */}
        <Card>
          <CardHeader>
            <CardTitle>Pipeline Velocity (Last {timelineStats.length} days)</CardTitle>
          </CardHeader>
          <CardContent>
            {timelineQuery.isLoading && <ChartSkeleton />}
            {timelineQuery.isError && <ErrorState message="Unable to load timeline data." />}
            {!timelineQuery.isLoading && !timelineQuery.isError && timelineStats.length === 0 && (
              <ChartSkeleton message="No timeline data for the selected filters." />
            )}
            {!timelineQuery.isLoading && !timelineQuery.isError && timelineStats.length > 0 && (
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={timelineStats}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="new_leads" name="New Leads" stroke="#6366f1" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="contacted" name="Contacted" stroke="#0ea5e9" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="converted" name="Converted" stroke="#10b981" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Rep Performance Table */}
        <Card>
          <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle>Rep Performance</CardTitle>
            <Button
              variant="outline"
              onClick={handleExportRepCsv}
              disabled={!reps.length || repPerformanceQuery.isLoading}
            >
              Export CSV
            </Button>
          </CardHeader>
          <CardContent className="overflow-x-auto">
            {repPerformanceQuery.isLoading && <ChartSkeleton />}
            {repPerformanceQuery.isError && <ErrorState message="Unable to load rep performance." />}
            {!repPerformanceQuery.isLoading && !repPerformanceQuery.isError && reps.length === 0 && (
              <ChartSkeleton message="No rep performance data for the selected filters." />
            )}
            {!repPerformanceQuery.isLoading && !repPerformanceQuery.isError && reps.length > 0 && (
              <table className="min-w-full divide-y divide-slate-200">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-600">
                      Sales Rep
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-600">
                      Leads Assigned
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-600">
                      Contacted
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-600">
                      Converted
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-600">
                      Conversion Rate
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-600">
                      Avg Response (hrs)
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 bg-white">
                  {reps.map((rep: RepPerformanceRow) => (
                    <tr
                      key={rep.rep_id}
                      className="cursor-pointer transition hover:bg-slate-50"
                      onClick={() => navigate(`/dashboard/manager?rep=${rep.rep_id}`)}
                    >
                      <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-slate-900">
                        {rep.rep_name}
                      </td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-600">
                        {rep.leads_assigned}
                      </td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-600">
                        {rep.leads_contacted}
                      </td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-600">
                        {rep.leads_converted}
                      </td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-600">
                        {rep.conversion_rate.toFixed(1)}%
                      </td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-600">
                        {rep.avg_response_time_hours.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}


