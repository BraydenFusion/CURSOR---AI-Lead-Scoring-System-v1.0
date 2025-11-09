import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import clsx from "clsx";
import {
  GripVertical,
  Pencil,
  Trash2,
  FlaskConical,
  CheckCircle2,
  AlertCircle,
  Play,
  Plus,
  RefreshCcw,
} from "lucide-react";

import { DashboardLayout } from "../components/layout/DashboardLayout";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import type {
  AssignmentRule,
  AssignmentRuleApplyResult,
  AssignmentRuleTestResult,
  AssignmentRuleType,
  EligibleRep,
  Lead,
  LeadListResponse,
} from "../types";
import {
  applyAssignmentRule,
  createAssignmentRule,
  deleteAssignmentRule,
  fetchAssignmentRules,
  fetchEligibleRepresentatives,
  testAssignmentRule,
  toggleAssignmentRule,
  updateAssignmentRule,
  type AssignmentRulePayload,
  type AssignmentRuleUpdatePayload,
} from "../services/assignmentRules";
import { apiClient } from "../services/api";

type ConditionsFormState = {
  lead_score_min: string;
  lead_score_max: string;
  sources: string;
  locations: string;
  days_of_week: number[];
  business_hours_only: boolean;
};

type RoundRobinLogicFormState = {
  type: "round_robin";
  eligible_reps: string[];
  max_leads_per_rep: string;
};

type TerritoryEntryFormState = {
  id: string;
  location: string;
  reps: string[];
};

type TerritoryLogicFormState = {
  type: "territory";
  eligible_reps: string[];
  territory_mapping: TerritoryEntryFormState[];
  max_leads_per_rep: string;
};

type WorkloadLogicFormState = {
  type: "workload";
  eligible_reps: string[];
  max_leads_per_rep: string;
};

type ScoreTierFormState = {
  id: string;
  min_score: string;
  max_score: string;
  reps: string[];
  max_leads_per_rep: string;
};

type ScoreBasedLogicFormState = {
  type: "score_based";
  tiers: ScoreTierFormState[];
  fallback_reps: string[];
  max_leads_per_rep: string;
};

type AssignmentRuleFormState = {
  id?: number;
  name: string;
  description: string;
  priority: number;
  active: boolean;
  rule_type: AssignmentRuleType;
  conditions: ConditionsFormState;
  assignment_logic:
    | RoundRobinLogicFormState
    | TerritoryLogicFormState
    | WorkloadLogicFormState
    | ScoreBasedLogicFormState;
};

type TestModalState = {
  open: boolean;
  ruleId: number | null;
  leadId: string;
  loading: boolean;
  applying: boolean;
  result: AssignmentRuleTestResult | null;
  applyResult: AssignmentRuleApplyResult | null;
  error: string | null;
};

const DAYS_OF_WEEK: Array<{ value: number; label: string }> = [
  { value: 1, label: "Mon" },
  { value: 2, label: "Tue" },
  { value: 3, label: "Wed" },
  { value: 4, label: "Thu" },
  { value: 5, label: "Fri" },
  { value: 6, label: "Sat" },
  { value: 7, label: "Sun" },
];

const SCORE_MIN = 0;
const SCORE_MAX = 100;

const createClientId = () =>
  typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : Math.random().toString(36).slice(2);

const defaultConditions: ConditionsFormState = {
  lead_score_min: "",
  lead_score_max: "",
  sources: "",
  locations: "",
  days_of_week: [1, 2, 3, 4, 5],
  business_hours_only: false,
};

const createDefaultLogic = (type: AssignmentRuleType):
  | RoundRobinLogicFormState
  | TerritoryLogicFormState
  | WorkloadLogicFormState
  | ScoreBasedLogicFormState => {
  switch (type) {
    case "round_robin":
      return { type, eligible_reps: [], max_leads_per_rep: "" };
    case "territory":
      return {
        type,
        eligible_reps: [],
        territory_mapping: [],
        max_leads_per_rep: "",
      };
    case "workload":
      return { type, eligible_reps: [], max_leads_per_rep: "" };
    case "score_based":
      return {
        type,
        tiers: [
          {
            id: createClientId(),
            min_score: "80",
            max_score: "100",
            reps: [],
            max_leads_per_rep: "",
          },
          {
            id: createClientId(),
            min_score: "0",
            max_score: "79",
            reps: [],
            max_leads_per_rep: "",
          },
        ],
        fallback_reps: [],
        max_leads_per_rep: "",
      };
  }
};

const createDefaultFormState = (): AssignmentRuleFormState => ({
  name: "",
  description: "",
  priority: 10,
  active: true,
  rule_type: "round_robin",
  conditions: { ...defaultConditions },
  assignment_logic: createDefaultLogic("round_robin"),
});

async function fetchLeadsForTesting(): Promise<Lead[]> {
  const { data } = await apiClient.get<LeadListResponse>("/leads", {
    params: { per_page: 100, sort: "score" },
  });
  return data.items;
}

function parseNumber(value: string): number | undefined {
  if (value === "" || value === null || value === undefined) return undefined;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : undefined;
}

function normalizeStringList(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

export function AssignmentRules() {
  const [formState, setFormState] = useState<AssignmentRuleFormState>(createDefaultFormState);
  const [formError, setFormError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [localRules, setLocalRules] = useState<AssignmentRule[]>([]);
  const [draggedRuleId, setDraggedRuleId] = useState<number | null>(null);
  const [testState, setTestState] = useState<TestModalState>({
    open: false,
    ruleId: null,
    leadId: "",
    loading: false,
    applying: false,
    result: null,
    applyResult: null,
    error: null,
  });

  const {
    data: rules,
    isLoading: rulesLoading,
    refetch: refetchRules,
  } = useQuery({
    queryKey: ["assignment-rules"],
    queryFn: fetchAssignmentRules,
  });

  const {
    data: eligibleReps,
    isLoading: repsLoading,
  } = useQuery({
    queryKey: ["assignment-rules", "eligible-reps"],
    queryFn: fetchEligibleRepresentatives,
  });

  const {
    data: leadsForTesting,
    isLoading: leadsLoading,
    refetch: refetchLeads,
  } = useQuery({
    queryKey: ["assignment-rules", "test-leads"],
    queryFn: fetchLeadsForTesting,
    enabled: testState.open,
  });

  useEffect(() => {
    if (rules) {
      setLocalRules(rules.slice().sort((a, b) => b.priority - a.priority));
    }
  }, [rules]);

  const resetForm = () => {
    setFormState(createDefaultFormState());
    setFormError(null);
  };

  const createMutation = useMutation({
    mutationFn: (payload: AssignmentRulePayload) => createAssignmentRule(payload),
    onSuccess: () => {
      setFeedback("Assignment rule created successfully.");
      resetForm();
      refetchRules();
    },
    onError: (error: any) => {
      setFormError(error?.response?.data?.detail ?? "Failed to create assignment rule.");
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ ruleId, payload }: { ruleId: number; payload: AssignmentRuleUpdatePayload }) =>
      updateAssignmentRule(ruleId, payload),
    onSuccess: () => {
      setFeedback("Assignment rule updated.");
      resetForm();
      refetchRules();
    },
    onError: (error: any) => {
      setFormError(error?.response?.data?.detail ?? "Failed to update assignment rule.");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (ruleId: number) => deleteAssignmentRule(ruleId),
    onSuccess: () => {
      setFeedback("Assignment rule deleted.");
      refetchRules();
    },
    onError: (error: any) => {
      setFeedback(error?.response?.data?.detail ?? "Failed to delete assignment rule.");
    },
  });

  const toggleMutation = useMutation({
    mutationFn: ({ ruleId, active }: { ruleId: number; active: boolean }) =>
      toggleAssignmentRule(ruleId, active),
    onSuccess: () => {
      refetchRules();
    },
    onError: (error: any) => {
      setFeedback(error?.response?.data?.detail ?? "Unable to toggle rule status.");
    },
  });

  const priorityMutation = useMutation({
    mutationFn: ({ ruleId, payload }: { ruleId: number; payload: AssignmentRuleUpdatePayload }) =>
      updateAssignmentRule(ruleId, payload),
    onSuccess: () => {
      refetchRules();
    },
    onError: (error: any) => {
      setFeedback(error?.response?.data?.detail ?? "Failed to update rule priorities.");
      refetchRules();
    },
  });

  const leadsOptions = useMemo(() => leadsForTesting ?? [], [leadsForTesting]);

  const currentEligibleReps = eligibleReps ?? [];

  const selectedRule = useMemo(
    () => (formState.id ? localRules.find((rule) => rule.id === formState.id) : null),
    [formState.id, localRules]
  );

  const handleRuleTypeChange = (ruleType: AssignmentRuleType) => {
    setFormState((prev) => ({
      ...prev,
      rule_type: ruleType,
      assignment_logic: createDefaultLogic(ruleType),
    }));
  };

  const handleConditionChange = (field: keyof ConditionsFormState, value: string | boolean | number[]) => {
    setFormState((prev) => ({
      ...prev,
      conditions: {
        ...prev.conditions,
        [field]: value,
      },
    }));
  };

  const toggleDayOfWeek = (day: number) => {
    setFormState((prev) => {
      const exists = prev.conditions.days_of_week.includes(day);
      const days = exists
        ? prev.conditions.days_of_week.filter((value) => value !== day)
        : [...prev.conditions.days_of_week, day];
      return {
        ...prev,
        conditions: {
          ...prev.conditions,
          days_of_week: days.sort(),
        },
      };
    });
  };

  const updateRoundRobinLogic = (changes: Partial<RoundRobinLogicFormState>) => {
    if (formState.assignment_logic.type !== "round_robin") return;
    setFormState((prev) => ({
      ...prev,
      assignment_logic: {
        ...prev.assignment_logic,
        ...changes,
      },
    }));
  };

  const updateTerritoryLogic = (changes: Partial<TerritoryLogicFormState>) => {
    if (formState.assignment_logic.type !== "territory") return;
    setFormState((prev) => ({
      ...prev,
      assignment_logic: {
        ...prev.assignment_logic,
        ...changes,
      },
    }));
  };

  const updateWorkloadLogic = (changes: Partial<WorkloadLogicFormState>) => {
    if (formState.assignment_logic.type !== "workload") return;
    setFormState((prev) => ({
      ...prev,
      assignment_logic: {
        ...prev.assignment_logic,
        ...changes,
      },
    }));
  };

  const updateScoreLogic = (changes: Partial<ScoreBasedLogicFormState>) => {
    if (formState.assignment_logic.type !== "score_based") return;
    setFormState((prev) => ({
      ...prev,
      assignment_logic: {
        ...prev.assignment_logic,
        ...changes,
      },
    }));
  };

  const addTerritoryRow = () => {
    if (formState.assignment_logic.type !== "territory") return;
    updateTerritoryLogic({
      territory_mapping: [
        ...formState.assignment_logic.territory_mapping,
        { id: createClientId(), location: "", reps: [] },
      ],
    });
  };

  const updateTerritoryRow = (rowId: string, changes: Partial<TerritoryEntryFormState>) => {
    if (formState.assignment_logic.type !== "territory") return;
    const updated = formState.assignment_logic.territory_mapping.map((entry) =>
      entry.id === rowId ? { ...entry, ...changes } : entry
    );
    updateTerritoryLogic({ territory_mapping: updated });
  };

  const removeTerritoryRow = (rowId: string) => {
    if (formState.assignment_logic.type !== "territory") return;
    const updated = formState.assignment_logic.territory_mapping.filter((entry) => entry.id !== rowId);
    updateTerritoryLogic({ territory_mapping: updated });
  };

  const addScoreTier = () => {
    if (formState.assignment_logic.type !== "score_based") return;
    updateScoreLogic({
      tiers: [
        ...formState.assignment_logic.tiers,
        { id: createClientId(), min_score: "0", max_score: "100", reps: [], max_leads_per_rep: "" },
      ],
    });
  };

  const updateScoreTier = (tierId: string, changes: Partial<ScoreTierFormState>) => {
    if (formState.assignment_logic.type !== "score_based") return;
    const updated = formState.assignment_logic.tiers.map((tier) =>
      tier.id === tierId ? { ...tier, ...changes } : tier
    );
    updateScoreLogic({ tiers: updated });
  };

  const removeScoreTier = (tierId: string) => {
    if (formState.assignment_logic.type !== "score_based") return;
    const updated = formState.assignment_logic.tiers.filter((tier) => tier.id !== tierId);
    updateScoreLogic({ tiers: updated });
  };

  const toggleRepSelection = (repId: string, selected: string[], onChange: (value: string[]) => void) => {
    if (selected.includes(repId)) {
      onChange(selected.filter((id) => id !== repId));
    } else {
      onChange([...selected, repId]);
    }
  };

  const populateFormFromRule = (rule: AssignmentRule) => {
    const conditions = rule.conditions || {};
    const logic = rule.assignment_logic || {};
    const ruleType = (rule.rule_type || logic.type || "round_robin") as AssignmentRuleType;

    const formConditions: ConditionsFormState = {
      lead_score_min: conditions.lead_score_min != null ? String(conditions.lead_score_min) : "",
      lead_score_max: conditions.lead_score_max != null ? String(conditions.lead_score_max) : "",
      sources: Array.isArray(conditions.sources) ? conditions.sources.join(", ") : "",
      locations: Array.isArray(conditions.locations) ? conditions.locations.join(", ") : "",
      days_of_week: Array.isArray(conditions.days_of_week) ? conditions.days_of_week : [],
      business_hours_only: Boolean(conditions.business_hours_only),
    };

    let assignmentLogic: AssignmentRuleFormState["assignment_logic"] = createDefaultLogic(ruleType);

    switch (ruleType) {
      case "round_robin":
        assignmentLogic = {
          type: "round_robin",
          eligible_reps: Array.isArray(logic.eligible_reps) ? (logic.eligible_reps as string[]) : [],
          max_leads_per_rep:
            logic.max_leads_per_rep != null && logic.max_leads_per_rep !== ""
              ? String(logic.max_leads_per_rep)
              : "",
        };
        break;
      case "territory":
        assignmentLogic = {
          type: "territory",
          eligible_reps: Array.isArray(logic.eligible_reps) ? (logic.eligible_reps as string[]) : [],
          max_leads_per_rep:
            logic.max_leads_per_rep != null && logic.max_leads_per_rep !== ""
              ? String(logic.max_leads_per_rep)
              : "",
          territory_mapping: Object.entries(logic.territory_mapping ?? {}).map(([location, reps]) => ({
            id: createClientId(),
            location,
            reps: Array.isArray(reps) ? (reps as string[]) : [],
          })),
        };
        break;
      case "workload":
        assignmentLogic = {
          type: "workload",
          eligible_reps: Array.isArray(logic.eligible_reps) ? (logic.eligible_reps as string[]) : [],
          max_leads_per_rep:
            logic.max_leads_per_rep != null && logic.max_leads_per_rep !== ""
              ? String(logic.max_leads_per_rep)
              : "",
        };
        break;
      case "score_based":
        assignmentLogic = {
          type: "score_based",
          tiers: Array.isArray(logic.tiers)
            ? (logic.tiers as Array<any>).map((tier) => ({
                id: createClientId(),
                min_score: tier.min_score != null ? String(tier.min_score) : "",
                max_score: tier.max_score != null ? String(tier.max_score) : "",
                reps: Array.isArray(tier.reps) ? (tier.reps as string[]) : [],
                max_leads_per_rep:
                  tier.max_leads_per_rep != null && tier.max_leads_per_rep !== ""
                    ? String(tier.max_leads_per_rep)
                    : "",
              }))
            : [],
          fallback_reps: Array.isArray(logic.fallback_reps) ? (logic.fallback_reps as string[]) : [],
          max_leads_per_rep:
            logic.max_leads_per_rep != null && logic.max_leads_per_rep !== ""
              ? String(logic.max_leads_per_rep)
              : "",
        };
        break;
    }

    setFormState({
      id: rule.id,
      name: rule.name,
      description: rule.description ?? "",
      priority: rule.priority ?? 10,
      active: rule.active ?? true,
      rule_type: ruleType,
      conditions: formConditions,
      assignment_logic: assignmentLogic,
    });
  };

  const validateForm = (): boolean => {
    setFormError(null);
    if (!formState.name.trim()) {
      setFormError("Rule name is required.");
      return false;
    }
    if (formState.priority < 1 || formState.priority > 10) {
      setFormError("Priority must be between 1 and 10.");
      return false;
    }

    const logic = formState.assignment_logic;
    switch (logic.type) {
      case "round_robin":
        if (logic.eligible_reps.length === 0) {
          setFormError("Select at least one eligible representative for round-robin rules.");
          return false;
        }
        break;
      case "territory":
        if (
          logic.territory_mapping.length === 0 ||
          logic.territory_mapping.some((entry) => !entry.location.trim() || entry.reps.length === 0)
        ) {
          setFormError("Territory rules require at least one territory with assigned representatives.");
          return false;
        }
        break;
      case "workload":
        if (logic.eligible_reps.length === 0) {
          setFormError("Select at least one representative for workload-based rules.");
          return false;
        }
        break;
      case "score_based":
        if (
          logic.tiers.length === 0 ||
          logic.tiers.some(
            (tier) =>
              tier.min_score === "" ||
              tier.max_score === "" ||
              Number(tier.min_score) > Number(tier.max_score) ||
              tier.reps.length === 0
          )
        ) {
          setFormError("Score-based rules require valid score tiers with representatives.");
          return false;
        }
        break;
    }

    return true;
  };

  const buildPayload = (): AssignmentRulePayload => {
    const conditionsPayload: Record<string, unknown> = {};

    const minScore = parseNumber(formState.conditions.lead_score_min);
    const maxScore = parseNumber(formState.conditions.lead_score_max);
    if (minScore !== undefined) conditionsPayload.lead_score_min = minScore;
    if (maxScore !== undefined) conditionsPayload.lead_score_max = maxScore;

    const sources = normalizeStringList(formState.conditions.sources);
    if (sources.length) conditionsPayload.sources = sources;

    const locations = normalizeStringList(formState.conditions.locations);
    if (locations.length) conditionsPayload.locations = locations;

    if (formState.conditions.days_of_week.length) {
      conditionsPayload.days_of_week = formState.conditions.days_of_week;
    }

    if (formState.conditions.business_hours_only) {
      conditionsPayload.business_hours_only = true;
    }

    const logic = formState.assignment_logic;
    let assignmentLogicPayload: Record<string, unknown> = { type: formState.rule_type };

    const maxLeads = parseNumber(
      "max_leads_per_rep" in logic ? logic.max_leads_per_rep : (logic as any).max_leads_per_rep
    );
    const includeMaxLeads = maxLeads !== undefined;

    switch (logic.type) {
      case "round_robin":
        assignmentLogicPayload = {
          type: "round_robin",
          eligible_reps: logic.eligible_reps,
          ...(includeMaxLeads ? { max_leads_per_rep: maxLeads } : {}),
        };
        break;
      case "territory":
        assignmentLogicPayload = {
          type: "territory",
          eligible_reps: logic.eligible_reps,
          territory_mapping: Object.fromEntries(
            logic.territory_mapping
              .filter((entry) => entry.location.trim() && entry.reps.length)
              .map((entry) => [entry.location.trim(), entry.reps])
          ),
          ...(includeMaxLeads ? { max_leads_per_rep: maxLeads } : {}),
        };
        break;
      case "workload":
        assignmentLogicPayload = {
          type: "workload",
          eligible_reps: logic.eligible_reps,
          ...(includeMaxLeads ? { max_leads_per_rep: maxLeads } : {}),
        };
        break;
      case "score_based":
        assignmentLogicPayload = {
          type: "score_based",
          tiers: logic.tiers.map((tier) => ({
            min_score: Number(tier.min_score),
            max_score: Number(tier.max_score),
            reps: tier.reps,
            ...(tier.max_leads_per_rep !== ""
              ? { max_leads_per_rep: Number(tier.max_leads_per_rep) }
              : {}),
          })),
          fallback_reps: logic.fallback_reps,
          ...(logic.max_leads_per_rep !== ""
            ? { max_leads_per_rep: Number(logic.max_leads_per_rep) }
            : {}),
        };
        break;
    }

    return {
      name: formState.name.trim(),
      description: formState.description.trim() || undefined,
      priority: formState.priority,
      active: formState.active,
      rule_type: formState.rule_type,
      conditions: conditionsPayload,
      assignment_logic: assignmentLogicPayload,
    };
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!validateForm()) return;

    const payload = buildPayload();

    if (formState.id) {
      updateMutation.mutate({ ruleId: formState.id, payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  const handleSaveAndTest = async () => {
    if (!validateForm()) return;
    const payload = buildPayload();

    try {
      if (formState.id) {
        await updateMutation.mutateAsync({ ruleId: formState.id, payload });
        openTestModal(formState.id);
      } else {
        const created = await createMutation.mutateAsync(payload);
        if (created?.id) {
          openTestModal(created.id);
        }
      }
    } catch (_error) {
      // errors handled in mutation
    }
  };

  const openTestModal = (ruleId: number) => {
    setTestState({
      open: true,
      ruleId,
      leadId: "",
      loading: false,
      applying: false,
      result: null,
      applyResult: null,
      error: null,
    });
    refetchLeads();
  };

  const closeTestModal = () => {
    setTestState({
      open: false,
      ruleId: null,
      leadId: "",
      loading: false,
      applying: false,
      result: null,
      applyResult: null,
      error: null,
    });
  };

  const handleRunTest = async () => {
    if (!testState.ruleId || !testState.leadId) return;
    setTestState((prev) => ({ ...prev, loading: true, error: null, result: null, applyResult: null }));
    try {
      const result = await testAssignmentRule(testState.ruleId, testState.leadId);
      setTestState((prev) => ({ ...prev, result, loading: false }));
    } catch (error: any) {
      setTestState((prev) => ({
        ...prev,
        loading: false,
        error: error?.response?.data?.detail ?? "Unable to test rule.",
      }));
    }
  };

  const handleApplyRule = async () => {
    if (!testState.ruleId || !testState.leadId) return;
    setTestState((prev) => ({ ...prev, applying: true, error: null }));
    try {
      const result = await applyAssignmentRule(testState.ruleId, testState.leadId);
      setTestState((prev) => ({ ...prev, applying: false, applyResult: result }));
      refetchRules();
    } catch (error: any) {
      setTestState((prev) => ({
        ...prev,
        applying: false,
        error: error?.response?.data?.detail ?? "Failed to apply assignment.",
      }));
    }
  };

  const handleEditRule = (rule: AssignmentRule) => {
    populateFormFromRule(rule);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleDeleteRule = (rule: AssignmentRule) => {
    const confirm = window.confirm(
      `Are you sure you want to delete the assignment rule "${rule.name}"? This action cannot be undone.`
    );
    if (!confirm) return;
    deleteMutation.mutate(rule.id);
  };

  const handleToggleRule = (rule: AssignmentRule) => {
    toggleMutation.mutate({ ruleId: rule.id, active: !rule.active });
  };

  const handleDragStart = (ruleId: number) => {
    setDraggedRuleId(ruleId);
  };

  const handleDragOver = (event: React.DragEvent<HTMLTableRowElement>) => {
    event.preventDefault();
  };

  const handleDrop = (targetRuleId: number) => {
    if (draggedRuleId === null || draggedRuleId === targetRuleId) return;

    const sourceIndex = localRules.findIndex((rule) => rule.id === draggedRuleId);
    const targetIndex = localRules.findIndex((rule) => rule.id === targetRuleId);
    if (sourceIndex === -1 || targetIndex === -1) return;

    const updated = [...localRules];
    const [moved] = updated.splice(sourceIndex, 1);
    updated.splice(targetIndex, 0, moved);

    const prioritized = updated.map((rule, index) => ({
      ...rule,
      priority: Math.max(1, Math.min(10, 10 - index)),
    }));

    setLocalRules(prioritized);
    setDraggedRuleId(null);

    prioritized.forEach((rule) => {
      priorityMutation.mutate({ ruleId: rule.id, payload: { priority: rule.priority } });
    });
  };

  const renderRepCheckboxes = (
    selected: string[],
    onToggle: (updated: string[]) => void,
    compact = false,
  ) => (
    <div className={clsx("grid gap-2", compact ? "grid-cols-1" : "grid-cols-1 sm:grid-cols-2")}>
      {currentEligibleReps.map((rep) => (
        <label key={rep.id} className="flex items-start gap-2 text-sm">
          <input
            type="checkbox"
            className="mt-1 h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
            checked={selected.includes(rep.id)}
            onChange={() => toggleRepSelection(rep.id, selected, onToggle)}
          />
          <span>
            <span className="font-medium text-slate-900">{rep.full_name}</span>
            <span className="block text-xs text-slate-500">
              {rep.email} · {rep.active_assignments} active leads
            </span>
          </span>
        </label>
      ))}
      {currentEligibleReps.length === 0 && (
        <p className="text-sm text-slate-500">No active sales representatives available.</p>
      )}
    </div>
  );

  const renderAssignmentLogicFields = () => {
    const logic = formState.assignment_logic;

    switch (logic.type) {
      case "round_robin":
        return (
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-slate-700">Eligible Representatives</label>
              <p className="text-xs text-slate-500 mb-2">
                Selected reps will receive leads in a rotating order.
              </p>
              {renderRepCheckboxes(logic.eligible_reps, (value) => updateRoundRobinLogic({ eligible_reps: value }))}
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">
                Max Leads Per Rep <span className="text-xs text-slate-500">(optional)</span>
              </label>
              <Input
                type="number"
                min={1}
                value={logic.max_leads_per_rep}
                onChange={(event) => updateRoundRobinLogic({ max_leads_per_rep: event.target.value })}
                placeholder="e.g. 20"
              />
            </div>
          </div>
        );

      case "territory":
        return (
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-slate-700">Default Eligible Representatives</label>
              <p className="text-xs text-slate-500 mb-2">
                These reps are used if a location is not covered by the territory map.
              </p>
              {renderRepCheckboxes(logic.eligible_reps, (value) => updateTerritoryLogic({ eligible_reps: value }))}
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-slate-700">Territory Mapping</label>
                <Button type="button" variant="outline" size="sm" onClick={addTerritoryRow}>
                  <Plus className="mr-2 h-4 w-4" /> Add Territory
                </Button>
              </div>
              {logic.territory_mapping.length === 0 && (
                <p className="text-sm text-slate-500">
                  Add one or more territories and assign representatives to each region.
                </p>
              )}
              <div className="space-y-3">
                {logic.territory_mapping.map((entry) => (
                  <div key={entry.id} className="rounded-lg border border-slate-200 bg-slate-50 p-4 space-y-3">
                    <div className="flex items-center justify-between gap-3">
                      <div className="flex-1">
                        <label className="text-xs font-medium uppercase text-slate-500">Location</label>
                        <Input
                          value={entry.location}
                          onChange={(event) => updateTerritoryRow(entry.id, { location: event.target.value })}
                          placeholder="e.g. New York"
                        />
                      </div>
                      <Button type="button" variant="ghost" size="sm" onClick={() => removeTerritoryRow(entry.id)}>
                        <Trash2 className="h-4 w-4 text-slate-500" />
                      </Button>
                    </div>
                    <div>
                      <label className="text-xs font-medium uppercase text-slate-500">
                        Assigned Representatives
                      </label>
                      {renderRepCheckboxes(entry.reps, (value) => updateTerritoryRow(entry.id, { reps: value }), true)}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-slate-700">
                Max Leads Per Rep <span className="text-xs text-slate-500">(optional)</span>
              </label>
              <Input
                type="number"
                min={1}
                value={logic.max_leads_per_rep}
                onChange={(event) => updateTerritoryLogic({ max_leads_per_rep: event.target.value })}
                placeholder="e.g. 15"
              />
            </div>
          </div>
        );

      case "workload":
        return (
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-slate-700">Eligible Representatives</label>
              <p className="text-xs text-slate-500 mb-2">
                Leads will be assigned to the rep with the fewest active leads.
              </p>
              {renderRepCheckboxes(logic.eligible_reps, (value) => updateWorkloadLogic({ eligible_reps: value }))}
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">
                Max Leads Per Rep <span className="text-xs text-slate-500">(optional)</span>
              </label>
              <Input
                type="number"
                min={1}
                value={logic.max_leads_per_rep}
                onChange={(event) => updateWorkloadLogic({ max_leads_per_rep: event.target.value })}
                placeholder="e.g. 30"
              />
            </div>
          </div>
        );

      case "score_based":
        return (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-slate-700">Score Tiers</label>
              <Button type="button" variant="outline" size="sm" onClick={addScoreTier}>
                <Plus className="mr-2 h-4 w-4" /> Add Tier
              </Button>
            </div>
            <div className="space-y-3">
              {logic.tiers.map((tier) => (
                <div key={tier.id} className="rounded-lg border border-slate-200 bg-slate-50 p-4 space-y-3">
                  <div className="grid gap-3 sm:grid-cols-2">
                    <div>
                      <label className="text-xs font-medium uppercase text-slate-500">Min Score</label>
                      <Input
                        type="number"
                        min={SCORE_MIN}
                        max={SCORE_MAX}
                        value={tier.min_score}
                        onChange={(event) => updateScoreTier(tier.id, { min_score: event.target.value })}
                      />
                    </div>
                    <div>
                      <label className="text-xs font-medium uppercase text-slate-500">Max Score</label>
                      <Input
                        type="number"
                        min={SCORE_MIN}
                        max={SCORE_MAX}
                        value={tier.max_score}
                        onChange={(event) => updateScoreTier(tier.id, { max_score: event.target.value })}
                      />
                    </div>
                    <div>
                      <label className="text-xs font-medium uppercase text-slate-500">
                        Tier Max Leads <span className="lowercase">(optional)</span>
                      </label>
                      <Input
                        type="number"
                        min={1}
                        value={tier.max_leads_per_rep}
                        onChange={(event) => updateScoreTier(tier.id, { max_leads_per_rep: event.target.value })}
                        placeholder="e.g. 10"
                      />
                    </div>
                    <div className="flex items-end justify-end">
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeScoreTier(tier.id)}
                        disabled={logic.tiers.length <= 1}
                      >
                        <Trash2 className="h-4 w-4 text-slate-500" />
                      </Button>
                    </div>
                  </div>
                  <div>
                    <label className="text-xs font-medium uppercase text-slate-500">
                      Assign To Representatives
                    </label>
                    {renderRepCheckboxes(tier.reps, (value) => updateScoreTier(tier.id, { reps: value }), true)}
                  </div>
                </div>
              ))}
            </div>

            <div>
              <label className="text-sm font-medium text-slate-700">Fallback Representatives</label>
              <p className="text-xs text-slate-500 mb-2">
                Used when a lead does not fit any defined score tier.
              </p>
              {renderRepCheckboxes(logic.fallback_reps, (value) => updateScoreLogic({ fallback_reps: value }))}
            </div>

            <div>
              <label className="text-sm font-medium text-slate-700">
                Global Max Leads Per Rep <span className="text-xs text-slate-500">(optional)</span>
              </label>
              <Input
                type="number"
                min={1}
                value={logic.max_leads_per_rep}
                onChange={(event) => updateScoreLogic({ max_leads_per_rep: event.target.value })}
                placeholder="e.g. 25"
              />
            </div>
          </div>
        );
    }
  };

  const renderTestModal = () => {
    if (!testState.open) return null;

    const rule = localRules.find((item) => item.id === testState.ruleId);

    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 px-4">
        <div className="w-full max-w-2xl rounded-lg bg-white shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Test Assignment Rule</h2>
              <p className="text-sm text-slate-500">
                {rule ? rule.name : "Unknown Rule"} — Select a lead to preview assignment results.
              </p>
            </div>
            <Button type="button" variant="ghost" onClick={closeTestModal}>
              ✕
            </Button>
          </div>

          <div className="space-y-6 px-6 py-5">
            <div>
              <label className="text-sm font-medium text-slate-700">Lead</label>
              <div className="mt-2">
                {leadsLoading ? (
                  <p className="text-sm text-slate-500">Loading leads...</p>
                ) : (
                  <select
                    className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={testState.leadId}
                    onChange={(event) =>
                      setTestState((prev) => ({ ...prev, leadId: event.target.value, applyResult: null, result: null }))
                    }
                  >
                    <option value="">Select a lead</option>
                    {leadsOptions.map((lead) => (
                      <option key={lead.id} value={lead.id}>
                        {lead.name} · {lead.email} · Score {lead.current_score}
                      </option>
                    ))}
                  </select>
                )}
              </div>
            </div>

            {testState.error && (
              <div className="flex items-start gap-2 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                <AlertCircle className="mt-0.5 h-4 w-4" />
                <span>{testState.error}</span>
              </div>
            )}

            {testState.result && (
              <div
                className={clsx(
                  "rounded-md border px-4 py-3 text-sm",
                  testState.result.matches ? "border-green-200 bg-green-50 text-green-700" : "border-amber-200 bg-amber-50 text-amber-700"
                )}
              >
                {testState.result.matches ? (
                  <div className="space-y-1">
                    <p className="font-semibold flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4" />
                      Rule conditions matched this lead.
                    </p>
                    {testState.result.assigned_user_id ? (
                      <p>
                        Suggested representative:{" "}
                        <span className="font-semibold">{testState.result.assigned_user_name ?? testState.result.assigned_user_id}</span>
                      </p>
                    ) : (
                      <p>No eligible representative found for this rule.</p>
                    )}
                  </div>
                ) : (
                  <div>
                    <p className="font-semibold">Rule did not match.</p>
                    <p className="text-sm">
                      {testState.result.reason ?? "The lead did not satisfy the rule conditions."}
                    </p>
                  </div>
                )}
              </div>
            )}

            {testState.applyResult && (
              <div
                className={clsx(
                  "rounded-md border px-4 py-3 text-sm",
                  testState.applyResult.success
                    ? "border-blue-200 bg-blue-50 text-blue-700"
                    : "border-red-200 bg-red-50 text-red-700"
                )}
              >
                {testState.applyResult.success ? (
                  <div>
                    <p className="font-semibold flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4" />
                      Assignment applied successfully.
                    </p>
                    <p>
                      Assigned to:{" "}
                      <span className="font-semibold">
                        {testState.applyResult.assigned_user_name ?? testState.applyResult.assigned_user_id}
                      </span>
                    </p>
                  </div>
                ) : (
                  <div>
                    <p className="font-semibold">Assignment failed.</p>
                    <p>{testState.applyResult.message ?? "Unable to assign the lead using this rule."}</p>
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="flex items-center justify-between gap-3 border-t border-slate-200 bg-slate-50 px-6 py-4">
            <div className="text-xs text-slate-500">
              Testing does not modify assignments until you apply the rule.
            </div>
            <div className="flex items-center gap-3">
              <Button type="button" variant="outline" onClick={closeTestModal}>
                Close
              </Button>
              <Button
                type="button"
                variant="outline"
                disabled={!testState.leadId || testState.loading}
                onClick={handleRunTest}
              >
                {testState.loading ? (
                  <RefreshCcw className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <FlaskConical className="mr-2 h-4 w-4" />
                )}
                Run Test
              </Button>
              <Button
                type="button"
                disabled={!testState.leadId || testState.applying}
                onClick={handleApplyRule}
              >
                {testState.applying ? (
                  <RefreshCcw className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Play className="mr-2 h-4 w-4" />
                )}
                Apply Assignment
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <DashboardLayout
      title="Assignment Rules"
      subtitle="Automate lead routing with flexible rule-based assignments."
    >
      <div className="space-y-6">
        {(rulesLoading || repsLoading) && (
          <div className="rounded-lg border border-slate-200 bg-white p-6 text-slate-500 shadow-sm">
            Loading assignment rules and representatives...
          </div>
        )}

        {feedback && (
          <div className="flex items-start gap-2 rounded-md border border-blue-200 bg-blue-50 px-3 py-2 text-sm text-blue-700">
            <CheckCircle2 className="mt-0.5 h-4 w-4" />
            <span>{feedback}</span>
          </div>
        )}

        <div className="grid gap-6 xl:grid-cols-[3fr,2fr]">
          <div className="space-y-4">
            <div className="rounded-lg border border-slate-200 bg-white shadow-sm">
              <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
                <h2 className="text-lg font-semibold text-slate-900">Rules</h2>
                <span className="text-xs text-slate-500">
                  Drag rows to reorder. Higher priority rules execute first.
                </span>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200 text-sm">
                  <thead className="bg-slate-50 text-xs uppercase tracking-wider text-slate-500">
                    <tr>
                      <th className="px-4 py-3 text-left">Order</th>
                      <th className="px-4 py-3 text-left">Name</th>
                      <th className="px-4 py-3 text-left">Type</th>
                      <th className="px-4 py-3 text-left">Priority</th>
                      <th className="px-4 py-3 text-left">Active</th>
                      <th className="px-4 py-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 bg-white">
                    {localRules.map((rule) => (
                      <tr
                        key={rule.id}
                        draggable
                        onDragStart={() => handleDragStart(rule.id)}
                        onDragOver={handleDragOver}
                        onDrop={() => handleDrop(rule.id)}
                        className="hover:bg-slate-50"
                      >
                        <td className="px-4 py-3 text-slate-500">
                          <div className="flex items-center gap-2">
                            <GripVertical className="h-4 w-4 text-slate-400" />
                            {rule.priority}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="font-medium text-slate-900">{rule.name}</div>
                          {rule.description && (
                            <div className="text-xs text-slate-500">{rule.description}</div>
                          )}
                        </td>
                        <td className="px-4 py-3 text-slate-600">
                          {rule.rule_type.replace("_", " ").toUpperCase()}
                        </td>
                        <td className="px-4 py-3 text-slate-600">{rule.priority}</td>
                        <td className="px-4 py-3">
                          <label className="inline-flex cursor-pointer items-center gap-2 text-xs font-medium">
                            <input
                              type="checkbox"
                              className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                              checked={rule.active}
                              onChange={() => handleToggleRule(rule)}
                            />
                            {rule.active ? "Active" : "Disabled"}
                          </label>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center justify-end gap-2">
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => openTestModal(rule.id)}
                            >
                              <FlaskConical className="h-4 w-4" />
                            </Button>
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => handleEditRule(rule)}
                            >
                              <Pencil className="h-4 w-4" />
                            </Button>
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteRule(rule)}
                            >
                              <Trash2 className="h-4 w-4 text-red-500" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                    {localRules.length === 0 && !rulesLoading && (
                      <tr>
                        <td colSpan={6} className="px-4 py-6 text-center text-sm text-slate-500">
                          No assignment rules yet. Use the builder to create your first rule.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div>
            <form
              onSubmit={handleSubmit}
              className="space-y-5 rounded-lg border border-slate-200 bg-white p-6 shadow-sm"
            >
              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  {formState.id ? "Edit Assignment Rule" : "Create Assignment Rule"}
                </h2>
                <p className="text-sm text-slate-500">
                  Define the conditions and logic for routing new leads to your team automatically.
                </p>
              </div>

              {formError && (
                <div className="flex items-start gap-2 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                  <AlertCircle className="mt-0.5 h-4 w-4" />
                  <span>{formError}</span>
                </div>
              )}

              <div className="space-y-1">
                <label className="text-sm font-medium text-slate-700">Rule Name</label>
                <Input
                  value={formState.name}
                  onChange={(event) => setFormState((prev) => ({ ...prev, name: event.target.value }))}
                  placeholder="e.g. Hot Leads - East Coast"
                  required
                />
              </div>

              <div className="space-y-1">
                <label className="text-sm font-medium text-slate-700">Description</label>
                <Textarea
                  value={formState.description}
                  onChange={(event) =>
                    setFormState((prev) => ({ ...prev, description: event.target.value }))
                  }
                  placeholder="Provide context for this rule (optional)"
                  rows={3}
                />
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="text-sm font-medium text-slate-700">Priority</label>
                  <Input
                    type="number"
                    min={1}
                    max={10}
                    value={formState.priority}
                    onChange={(event) =>
                      setFormState((prev) => ({
                        ...prev,
                        priority: Number(event.target.value),
                      }))
                    }
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    Higher numbers run first. Allowed range: 1-10.
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-700">Status</label>
                  <div className="mt-1 flex items-center gap-2">
                    <input
                      type="checkbox"
                      className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                      checked={formState.active}
                      onChange={(event) =>
                        setFormState((prev) => ({ ...prev, active: event.target.checked }))
                      }
                    />
                    <span className="text-sm text-slate-600">
                      {formState.active ? "Active" : "Disabled"}
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-sm font-medium text-slate-700">Rule Type</label>
                <select
                  className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={formState.rule_type}
                  onChange={(event) => handleRuleTypeChange(event.target.value as AssignmentRuleType)}
                >
                  <option value="round_robin">Round Robin</option>
                  <option value="territory">Territory</option>
                  <option value="workload">Workload</option>
                  <option value="score_based">Score-Based</option>
                </select>
              </div>

              <div className="space-y-4 rounded-lg border border-slate-200 bg-slate-50 p-4">
                <h3 className="text-sm font-semibold text-slate-800">Conditions</h3>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label className="text-xs font-medium uppercase text-slate-500">
                      Minimum Score
                    </label>
                    <Input
                      type="number"
                      min={SCORE_MIN}
                      max={SCORE_MAX}
                      value={formState.conditions.lead_score_min}
                      onChange={(event) =>
                        handleConditionChange("lead_score_min", event.target.value)
                      }
                      placeholder="e.g. 70"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium uppercase text-slate-500">Maximum Score</label>
                    <Input
                      type="number"
                      min={SCORE_MIN}
                      max={SCORE_MAX}
                      value={formState.conditions.lead_score_max}
                      onChange={(event) =>
                        handleConditionChange("lead_score_max", event.target.value)
                      }
                      placeholder="e.g. 100"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium uppercase text-slate-500">
                      Sources <span className="lowercase">(comma separated)</span>
                    </label>
                    <Input
                      value={formState.conditions.sources}
                      onChange={(event) => handleConditionChange("sources", event.target.value)}
                      placeholder="Website, Referral"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium uppercase text-slate-500">
                      Locations <span className="lowercase">(comma separated)</span>
                    </label>
                    <Input
                      value={formState.conditions.locations}
                      onChange={(event) => handleConditionChange("locations", event.target.value)}
                      placeholder="New York, California"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-xs font-medium uppercase text-slate-500">Days of Week</label>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {DAYS_OF_WEEK.map((day) => (
                      <button
                        key={day.value}
                        type="button"
                        className={clsx(
                          "rounded-md border px-3 py-1 text-xs font-medium transition",
                          formState.conditions.days_of_week.includes(day.value)
                            ? "border-blue-500 bg-blue-50 text-blue-600"
                            : "border-slate-200 text-slate-500 hover:border-slate-300"
                        )}
                        onClick={() => toggleDayOfWeek(day.value)}
                      >
                        {day.label}
                      </button>
                    ))}
                  </div>
                </div>
                <label className="inline-flex items-center gap-2 text-xs font-medium uppercase text-slate-500">
                  <input
                    type="checkbox"
                    className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                    checked={formState.conditions.business_hours_only}
                    onChange={(event) =>
                      handleConditionChange("business_hours_only", event.target.checked)
                    }
                  />
                  Business Hours Only (9am-6pm UTC)
                </label>
              </div>

              <div className="space-y-4 rounded-lg border border-slate-200 bg-slate-50 p-4">
                <h3 className="text-sm font-semibold text-slate-800">Assignment Logic</h3>
                {renderAssignmentLogicFields()}
              </div>

              <div className="flex flex-wrap items-center justify-end gap-3">
                {selectedRule && (
                  <Button type="button" variant="ghost" onClick={resetForm}>
                    Cancel Edit
                  </Button>
                )}
                <Button type="button" variant="outline" onClick={handleSaveAndTest} disabled={createMutation.isLoading || updateMutation.isLoading}>
                  Save & Test
                </Button>
                <Button type="submit" disabled={createMutation.isLoading || updateMutation.isLoading}>
                  {formState.id ? "Update Rule" : "Create Rule"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>

      {renderTestModal()}
    </DashboardLayout>
  );
}
