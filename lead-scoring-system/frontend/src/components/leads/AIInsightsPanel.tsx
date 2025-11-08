import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Sparkles,
  CalendarPlus,
  RefreshCcw,
  AlertTriangle,
  Mail,
  Clipboard,
  ListChecks,
  Printer,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";
import { fetchAIInsights, fetchNextBestActions, generateEmailTemplate } from "../../services/ai";
import type {
  AIInsight,
  AIActionItem,
  EmailTemplateResponsePayload,
  NextBestActionResponse,
} from "../../types";

type Props = {
  leadId: string;
  leadName: string;
};

const EMAIL_TYPES = [
  { value: "initial_outreach", label: "Initial Outreach" },
  { value: "follow_up", label: "Follow Up" },
  { value: "demo_invite", label: "Demo Invite" },
  { value: "pricing_discussion", label: "Pricing Discussion" },
] as const;

function formatDateTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString();
}

function levelToPercentage(level: string) {
  switch (level) {
    case "high":
      return 100;
    case "medium":
      return 66;
    case "low":
      return 33;
    default:
      return 50;
  }
}

export function AIInsightsPanel({ leadId, leadName }: Props) {
  const queryClient = useQueryClient();
  const [emailType, setEmailType] = useState<typeof EMAIL_TYPES[number]["value"]>("initial_outreach");
  const [emailDraft, setEmailDraft] = useState<EmailTemplateResponsePayload | null>(null);
  const [copyStatus, setCopyStatus] = useState<string | null>(null);
  const [completedActions, setCompletedActions] = useState<Record<number, boolean>>({});
  const [expandedPoints, setExpandedPoints] = useState<Record<number, boolean>>({});
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const insightsQuery = useQuery({
    queryKey: ["ai-insights", leadId],
    queryFn: async () => {
      setErrorMessage(null);
      return fetchAIInsights(leadId);
    },
    staleTime: 1000 * 60 * 10,
    retry: (failureCount, error: any) => {
      const status = error?.response?.status;
      // For configuration or rate limit failures, surface immediately
      if (status === 503 || status === 429) {
        return false;
      }
      return failureCount < 2;
    },
    onError: (error: any) => {
      const status = error?.response?.status;
      if (status === 503) {
        setErrorMessage("AI insights are unavailable because the OpenAI API key is not configured.");
      } else if (status === 429) {
        setErrorMessage("Rate limit reached. Please try again in a little while.");
      } else if (status === 404) {
        setErrorMessage("Lead not found.");
      } else {
        setErrorMessage("Unable to load AI insights. Please try again later.");
      }
    },
  });

  const nextActionsMutation = useMutation({
    mutationFn: fetchNextBestActions,
    onSuccess: (data: NextBestActionResponse) => {
      queryClient.setQueryData<AIInsight | undefined>(["ai-insights", leadId], (previous) => {
        if (!previous) return previous;
        return {
          ...previous,
          recommended_actions: data.recommended_actions,
          generated_at: data.generated_at,
        };
      });
      setCompletedActions({});
    },
    onError: (error: any) => {
      const status = error?.response?.status;
      if (status === 429) {
        setErrorMessage("Rate limit reached for next best action. Please wait before trying again.");
      } else {
        setErrorMessage("Unable to refresh next best actions right now.");
      }
    },
  });

  const emailMutation = useMutation({
    mutationFn: () =>
      generateEmailTemplate({
        lead_id: leadId,
        email_type: emailType,
      }),
    onSuccess: (data) => {
      setEmailDraft(data);
      setCopyStatus(null);
    },
    onError: (error: any) => {
      const status = error?.response?.status;
      if (status === 503) {
        setErrorMessage("Email assistant is unavailable because the OpenAI API key is not configured.");
      } else if (status === 429) {
        setErrorMessage("Email assistant rate limit reached. Please wait before generating another email.");
      } else {
        setErrorMessage("Unable to generate email template right now.");
      }
    },
  });

  const insights = insightsQuery.data;
  const isLoading = insightsQuery.isLoading || insightsQuery.isFetching || nextActionsMutation.isPending;

  const conversionLevel = insights?.conversion_probability?.level ?? "unknown";
  const conversionConfidence = insights?.conversion_probability?.confidence ?? null;

  useEffect(() => {
    setCompletedActions({});
    setExpandedPoints({});
  }, [leadId, insights?.generated_at]);

  const handleMarkAction = (index: number, action: AIActionItem) => {
    setCompletedActions((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  const handleToggleTalkingPoint = (index: number) => {
    setExpandedPoints((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  const handleAddToCalendar = (action: AIActionItem) => {
    const title = encodeURIComponent(`${action.title} - ${leadName}`);
    const details = encodeURIComponent(action.description);
    const url = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&details=${details}`;
    window.open(url, "_blank", "noopener,noreferrer");
  };

  const handleCopyEmail = async () => {
    if (!emailDraft) return;
    try {
      await navigator.clipboard.writeText(`${emailDraft.subject}\n\n${emailDraft.body}`);
      setCopyStatus("Copied!");
    } catch (error) {
      setCopyStatus("Copy failed. Please try manually.");
    }
  };

  const handleSendEmailClient = () => {
    if (!emailDraft) return;
    const subject = encodeURIComponent(emailDraft.subject);
    const body = encodeURIComponent(emailDraft.body);
    window.location.href = `mailto:?subject=${subject}&body=${body}`;
  };

  const conversionGaugeStyle = useMemo(
    () => ({
      width: `${levelToPercentage(conversionLevel)}%`,
    }),
    [conversionLevel],
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-indigo-500" />
          <h2 className="text-xl font-semibold text-slate-900">AI Insights</h2>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => insightsQuery.refetch()}
            disabled={insightsQuery.isFetching}
          >
            <RefreshCcw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => nextActionsMutation.mutate(leadId)}
            disabled={nextActionsMutation.isPending}
          >
            <ListChecks className="mr-2 h-4 w-4" />
            New Actions
          </Button>
        </div>
      </div>

      {errorMessage && (
        <div className="flex items-start gap-2 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          <AlertTriangle className="mt-0.5 h-4 w-4" />
          <span>{errorMessage}</span>
        </div>
      )}

      {isLoading && (
        <Card>
          <CardContent className="flex items-center gap-3 py-10">
            <Sparkles className="h-6 w-6 animate-spin text-indigo-500" />
            <div>
              <p className="font-semibold text-slate-800">AI is analyzing this lead...</p>
              <p className="text-sm text-slate-500">Insights typically generate within a few seconds.</p>
            </div>
          </CardContent>
        </Card>
      )}

      {insights && !isLoading && (
        <>
          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Lead Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-slate-700">{insights.summary}</p>
                <div className="text-sm text-slate-500">
                  <p>
                    Confidence:{" "}
                    {insights.summary_confidence
                      ? `${Math.round(insights.summary_confidence * 100)}%`
                      : "Not provided"}
                  </p>
                  <p>Generated: {formatDateTime(insights.generated_at)}</p>
                  {typeof insights.estimated_cost === "number" && (
                    <p>Estimated cost: ${insights.estimated_cost.toFixed(4)}</p>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Conversion Probability</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="h-2 w-full rounded-full bg-slate-200">
                    <div
                      className="h-2 rounded-full bg-gradient-to-r from-amber-400 via-amber-500 to-green-500"
                      style={conversionGaugeStyle}
                    />
                  </div>
                  <div className="flex items-center justify-between text-sm text-slate-600">
                    <span className="uppercase tracking-wide text-xs text-slate-500">Probability</span>
                    <span className="font-semibold text-slate-800">{conversionLevel.toUpperCase()}</span>
                  </div>
                  {conversionConfidence !== null && (
                    <p className="text-sm text-slate-500">
                      Confidence: {Math.round(conversionConfidence * 100)}%
                    </p>
                  )}
                </div>
                <div className="space-y-2">
                  <p className="text-sm font-medium text-slate-700">AI Reasoning</p>
                  <ul className="list-disc space-y-1 pl-5 text-sm text-slate-600">
                    {insights.conversion_probability.reasoning.length === 0 ? (
                      <li>No reasoning provided.</li>
                    ) : (
                      insights.conversion_probability.reasoning.map((reason, index) => (
                        <li key={index}>{reason}</li>
                      ))
                    )}
                  </ul>
                </div>
                {insights.conversion_probability.comparison_to_similar && (
                  <p className="rounded-md bg-indigo-50 p-3 text-sm text-indigo-700">
                    {insights.conversion_probability.comparison_to_similar}
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Recommended Next Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {insights.recommended_actions.length === 0 && (
                <p className="text-sm text-slate-500">No recommended actions available.</p>
              )}
              {insights.recommended_actions.map((action, index) => {
                const isDone = completedActions[index] ?? false;
                return (
                  <div
                    key={`${action.title}-${index}`}
                    className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
                  >
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <p className="text-base font-semibold text-slate-900">{action.title}</p>
                        <p className="text-sm text-slate-600">{action.description}</p>
                      </div>
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                          Priority {action.priority ?? 3}
                        </span>
                        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                          {action.time_estimate || "30 minutes"}
                        </span>
                      </div>
                    </div>
                    <div className="mt-3 flex flex-wrap items-center gap-2">
                      <label className="inline-flex items-center gap-2 text-sm text-slate-600">
                        <input
                          type="checkbox"
                          checked={isDone}
                          onChange={() => handleMarkAction(index, action)}
                          className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                        />
                        Mark as done
                      </label>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleAddToCalendar(action)}
                        className="flex items-center gap-2"
                      >
                        <CalendarPlus className="h-4 w-4" />
                        Add to calendar
                      </Button>
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>AI Email Assistant</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-slate-700">Email Type</label>
                  <select
                    className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    value={emailType}
                    onChange={(event) =>
                      setEmailType(event.target.value as typeof EMAIL_TYPES[number]["value"])
                    }
                  >
                    {EMAIL_TYPES.map((option) => (
                      <option value={option.value} key={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
                <Button
                  onClick={() => emailMutation.mutate()}
                  disabled={emailMutation.isPending}
                  className="flex items-center gap-2"
                >
                  <Mail className="h-4 w-4" />
                  {emailMutation.isPending ? "Generating..." : "Generate Email"}
                </Button>
              </div>

              {emailDraft && (
                <div className="space-y-3">
                  <div>
                    <p className="text-sm font-semibold text-slate-700">Subject</p>
                    <p className="text-sm text-slate-600">{emailDraft.subject}</p>
                  </div>
                  <Textarea
                    value={emailDraft.body}
                    onChange={(event) =>
                      setEmailDraft((prev) =>
                        prev ? { ...prev, body: event.target.value } : prev,
                      )
                    }
                    rows={8}
                    className="font-mono text-sm"
                  />
                  {emailDraft.call_to_action && (
                    <div>
                      <p className="text-sm font-semibold text-slate-700">Call to Action</p>
                      <p className="text-sm text-slate-600">{emailDraft.call_to_action}</p>
                    </div>
                  )}
                  <div className="flex flex-wrap items-center gap-2">
                    <Button variant="outline" size="sm" onClick={handleCopyEmail} className="flex items-center gap-2">
                      <Clipboard className="h-4 w-4" />
                      Copy to clipboard
                    </Button>
                    <Button variant="outline" size="sm" onClick={handleSendEmailClient}>
                      Send via email client
                    </Button>
                    {copyStatus && <span className="text-xs text-slate-500">{copyStatus}</span>}
                  </div>
                  <p className="text-xs text-slate-500">
                    Generated at {formatDateTime(emailDraft.generated_at)}{" "}
                    {typeof emailDraft.estimated_cost === "number" && (
                      <>· Estimated cost ${emailDraft.estimated_cost.toFixed(4)}</>
                    )}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Key Talking Points</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {insights.talking_points.length === 0 && (
                <p className="text-sm text-slate-500">No talking points available.</p>
              )}
              {insights.talking_points.map((point, index) => {
                const isExpanded = expandedPoints[index] ?? false;
                return (
                  <div key={`${point.title}-${index}`} className="rounded border border-slate-200 bg-white">
                    <button
                      type="button"
                      onClick={() => handleToggleTalkingPoint(index)}
                      className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-semibold text-slate-800 hover:bg-slate-50"
                    >
                      <span>{point.title}</span>
                      <span>{isExpanded ? "−" : "+"}</span>
                    </button>
                    {isExpanded && (
                      <div className="border-t border-slate-100 px-4 py-3 text-sm text-slate-600">
                        {point.details}
                      </div>
                    )}
                  </div>
                );
              })}
              <div className="flex items-center gap-2 pt-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => window.print()}
                  className="flex items-center gap-2"
                >
                  <Printer className="h-4 w-4" />
                  Export / Print
                </Button>
                <p className="text-xs text-slate-500">
                  Tip: Export to PDF via your browser&apos;s print dialog.
                </p>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
