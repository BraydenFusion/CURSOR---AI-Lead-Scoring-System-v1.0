import { Dialog } from "@headlessui/react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Activity,
  CheckCircle2,
  Plus,
  RefreshCw,
  ToggleLeft,
  ToggleRight,
  Trash,
  Webhook as WebhookIcon,
} from "lucide-react";
import { Fragment, FormEvent, useEffect, useMemo, useState } from "react";
import { formatDistanceToNow } from "date-fns";

import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import {
  Webhook,
  WebhookDeliveryListResponse,
  WebhookEvent,
  WebhookListResponse,
  WebhookSecretResponse,
} from "../types";
import {
  createWebhook,
  deleteWebhook,
  fetchWebhookDeliveries,
  fetchWebhooks,
  testWebhook,
  updateWebhook,
} from "../services/developers";

type WebhookFormState = {
  url: string;
  events: WebhookEvent[];
  secret?: string;
  active: boolean;
};

const EVENT_LABELS: Record<WebhookEvent, string> = {
  "lead.created": "Lead created",
  "lead.updated": "Lead updated",
  "lead.scored": "Lead scored",
  "lead.assigned": "Lead assigned",
  "lead.converted": "Lead converted",
  "note.added": "Note added",
  "activity.created": "Activity created",
  "*": "All events",
};

export function WebhooksPage() {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formState, setFormState] = useState<WebhookFormState>({
    url: "",
    events: ["lead.created"],
    secret: "",
    active: true,
  });
  const [editingWebhook, setEditingWebhook] = useState<Webhook | null>(null);
  const [createdSecret, setCreatedSecret] = useState<string | null>(null);
  const [selectedWebhookId, setSelectedWebhookId] = useState<number | null>(null);

  const webhooksQuery = useQuery<WebhookListResponse>({
    queryKey: ["webhooks"],
    queryFn: fetchWebhooks,
  });

  const deliveriesQuery = useQuery<WebhookDeliveryListResponse>({
    queryKey: ["webhookDeliveries", selectedWebhookId],
    queryFn: () => fetchWebhookDeliveries(selectedWebhookId!),
    enabled: Boolean(selectedWebhookId),
  });

  const saveMutation = useMutation({
    mutationFn: async (payload: WebhookFormState) => {
      if (editingWebhook) {
        await updateWebhook(editingWebhook.id, payload);
        return null;
      }
      const response = await createWebhook(payload);
      return response as WebhookSecretResponse;
    },
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ["webhooks"] });
      if (response) {
        setCreatedSecret(response.secret);
      }
      setIsModalOpen(false);
      setEditingWebhook(null);
      setFormState({ url: "", events: ["lead.created"], secret: "", active: true });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteWebhook,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["webhooks"] });
      if (selectedWebhookId) {
        queryClient.removeQueries({ queryKey: ["webhookDeliveries", selectedWebhookId] });
        setSelectedWebhookId(null);
      }
    },
  });

  const testMutation = useMutation({
    mutationFn: ({ webhookId, event }: { webhookId: number; event?: string }) =>
      testWebhook(webhookId, { event }),
  });

  const allEvents = useMemo(() => Object.keys(EVENT_LABELS) as WebhookEvent[], []);

  const openModalForCreate = () => {
    setEditingWebhook(null);
    setFormState({ url: "", events: ["lead.created"], secret: "", active: true });
    setIsModalOpen(true);
    setCreatedSecret(null);
  };

  const openModalForEdit = (webhook: Webhook) => {
    setEditingWebhook(webhook);
    setFormState({
      url: webhook.url,
      events: webhook.events,
      secret: "",
      active: webhook.active,
    });
    setIsModalOpen(true);
    setCreatedSecret(null);
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!formState.url) return;
    saveMutation.mutate(formState);
  };

  const toggleEvent = (eventName: WebhookEvent) => {
    setFormState((prev) => {
      if (eventName === "*") {
        return { ...prev, events: ["*"] };
      }
      const events = prev.events.includes(eventName)
        ? prev.events.filter((item) => item !== eventName)
        : [...prev.events.filter((item) => item !== "*"), eventName];
      return { ...prev, events };
    });
  };

  const generateSecret = () => {
    if (window.crypto?.randomUUID) {
      setFormState((prev) => ({ ...prev, secret: window.crypto.randomUUID().replace(/-/g, "") }));
    } else {
      const random = Math.random().toString(36).slice(2) + Math.random().toString(36).slice(2);
      setFormState((prev) => ({ ...prev, secret: random }));
    }
  };

  useEffect(() => {
    if (webhooksQuery.data?.items.length && !selectedWebhookId) {
      setSelectedWebhookId(webhooksQuery.data.items[0].id);
    }
  }, [webhooksQuery.data?.items, selectedWebhookId]);

  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Webhooks</h1>
          <p className="mt-1 text-sm text-slate-500">
            Receive real-time notifications when key events occur. Use secrets to verify payload signatures.
          </p>
        </div>
        <Button onClick={openModalForCreate} className="inline-flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Create Webhook
        </Button>
      </header>

      {createdSecret && (
        <div className="rounded-lg border border-sky-200 bg-sky-50 p-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="flex items-center gap-2 text-sm font-semibold text-sky-800">
                <WebhookIcon className="h-4 w-4" />
                Webhook Secret Created
              </h2>
              <p className="mt-2 text-sm text-sky-700">Copy this secret for signature verification. It will not be displayed again.</p>
              <pre className="mt-3 overflow-x-auto rounded-md bg-white px-3 py-2 text-sm text-slate-900 shadow-inner">{createdSecret}</pre>
            </div>
            <Button variant="outline" onClick={() => navigator.clipboard.writeText(createdSecret)}>
              Copy
            </Button>
          </div>
        </div>
      )}

      <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">URL</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Events</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Status</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {webhooksQuery.isLoading && (
                  <tr>
                    <td colSpan={4} className="px-4 py-6 text-center text-sm text-slate-500">
                      Loading webhooks…
                    </td>
                  </tr>
                )}
                {webhooksQuery.data?.items.length === 0 && !webhooksQuery.isLoading && (
                  <tr>
                    <td colSpan={4} className="px-4 py-6 text-center text-sm text-slate-500">
                      No webhooks configured. Create one to receive event notifications.
                    </td>
                  </tr>
                )}
                {webhooksQuery.data?.items.map((webhook) => {
                  const isActive = selectedWebhookId === webhook.id;
                  return (
                    <tr
                      key={webhook.id}
                      className={isActive ? "bg-slate-50/70" : ""}
                    >
                      <td className="px-4 py-3 text-sm text-blue-600">
                        <button
                          className="text-left hover:underline"
                          onClick={() => setSelectedWebhookId(webhook.id)}
                        >
                          {webhook.url}
                        </button>
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-600">
                        <div className="flex flex-wrap gap-2">
                          {webhook.events.map((event) => (
                            <span key={event} className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
                              {EVENT_LABELS[event]}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-600">
                        <div className="inline-flex items-center gap-2">
                          {webhook.active ? (
                            <>
                              <ToggleRight className="h-5 w-5 text-emerald-500" />
                              <span className="text-emerald-600">Active</span>
                            </>
                          ) : (
                            <>
                              <ToggleLeft className="h-5 w-5 text-slate-400" />
                              <span className="text-slate-500">Disabled</span>
                            </>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-right text-sm">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() =>
                              updateWebhook(webhook.id, {
                                url: webhook.url,
                                events: webhook.events,
                                active: !webhook.active,
                              }).then(() => queryClient.invalidateQueries({ queryKey: ["webhooks"] }))
                            }
                          >
                            Toggle
                          </Button>
                          <Button variant="outline" size="sm" onClick={() => openModalForEdit(webhook)}>
                            Edit
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            disabled={testMutation.isLoading}
                            onClick={() => testMutation.mutate({ webhookId: webhook.id })}
                          >
                            Test
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-600 hover:bg-red-50 hover:text-red-700"
                            disabled={deleteMutation.isLoading}
                            onClick={() => deleteMutation.mutate(webhook.id)}
                          >
                            <Trash className="mr-1 h-4 w-4" />
                            Delete
                          </Button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 px-4 py-3">
            <h2 className="text-sm font-semibold text-slate-900">Recent Deliveries</h2>
            <p className="text-xs text-slate-500">
              Monitor webhook delivery status. Failed deliveries can be retried after addressing the issue.
            </p>
          </div>
          <div className="max-h-[420px] overflow-y-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Event</th>
                  <th className="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Status</th>
                  <th className="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Response</th>
                  <th className="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {!selectedWebhookId && (
                  <tr>
                    <td colSpan={4} className="px-4 py-6 text-center text-sm text-slate-500">
                      Select a webhook to view recent deliveries.
                    </td>
                  </tr>
                )}
                {deliveriesQuery.isLoading && (
                  <tr>
                    <td colSpan={4} className="px-4 py-6 text-center text-sm text-slate-500">
                      Loading deliveries…
                    </td>
                  </tr>
                )}
                {deliveriesQuery.data?.deliveries.length === 0 && !deliveriesQuery.isLoading && (
                  <tr>
                    <td colSpan={4} className="px-4 py-6 text-center text-sm text-slate-500">
                      No deliveries recorded yet.
                    </td>
                  </tr>
                )}
                {deliveriesQuery.data?.deliveries.map((delivery) => (
                  <tr key={delivery.id}>
                    <td className="px-4 py-2 text-sm text-slate-700">{delivery.event}</td>
                    <td className="px-4 py-2 text-sm">
                      <span
                        className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold ${
                          delivery.status === "success"
                            ? "bg-emerald-100 text-emerald-700"
                            : "bg-red-100 text-red-700"
                        }`}
                      >
                        {delivery.status === "success" ? (
                          <CheckCircle2 className="h-3 w-3" />
                        ) : (
                          <Activity className="h-3 w-3" />
                        )}
                        {delivery.status}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-sm text-slate-600">
                      {delivery.response_code ? `${delivery.response_code}` : "—"}
                    </td>
                    <td className="px-4 py-2 text-sm text-slate-600">
                      {formatDistanceToNow(new Date(delivery.created_at), { addSuffix: true })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {selectedWebhookId && (
            <div className="flex justify-end border-t border-slate-200 px-4 py-3">
              <Button
                variant="outline"
                size="sm"
                onClick={() => deliveriesQuery.refetch()}
                disabled={deliveriesQuery.isFetching}
                className="inline-flex items-center gap-2"
              >
                <RefreshCw className="h-4 w-4" />
                Refresh
              </Button>
            </div>
          )}
        </div>
      </section>

      <Dialog open={isModalOpen} onClose={() => setIsModalOpen(false)} as={Fragment}>
        <div className="fixed inset-0 z-30 flex items-center justify-center bg-slate-900/40 px-4 py-8">
          <Dialog.Panel className="w-full max-w-xl rounded-xl bg-white p-6 shadow-xl">
            <Dialog.Title className="text-lg font-semibold text-slate-900">
              {editingWebhook ? "Edit Webhook" : "Create Webhook"}
            </Dialog.Title>
            <form onSubmit={handleSubmit} className="mt-4 space-y-4">
              <div>
                <label className="text-sm font-medium text-slate-700">Destination URL</label>
                <Input
                  value={formState.url}
                  onChange={(event) => setFormState((prev) => ({ ...prev, url: event.target.value }))}
                  placeholder="https://example.com/webhooks/lead"
                  required
                  className="mt-1"
                />
                <p className="mt-1 text-xs text-slate-500">Must be an HTTPS endpoint that accepts POST requests.</p>
              </div>

              <div>
                <span className="text-sm font-medium text-slate-700">Subscribed Events</span>
                <div className="mt-2 grid grid-cols-1 gap-2 md:grid-cols-2">
                  {allEvents.map((eventName) => (
                    <label
                      key={eventName}
                      className="flex cursor-pointer items-center gap-2 rounded-md border border-slate-200 px-3 py-2 text-sm transition hover:border-slate-300"
                    >
                      <input
                        type="checkbox"
                        className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                        checked={formState.events.includes(eventName)}
                        onChange={() => toggleEvent(eventName)}
                      />
                      <span>{EVENT_LABELS[eventName]}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-slate-700">Secret (optional)</label>
                <div className="mt-1 flex gap-2">
                  <Input
                    value={formState.secret ?? ""}
                    onChange={(event) => setFormState((prev) => ({ ...prev, secret: event.target.value }))}
                    placeholder="Auto-generated if left blank"
                  />
                  <Button type="button" variant="outline" onClick={generateSecret}>
                    Generate
                  </Button>
                </div>
                <p className="mt-1 text-xs text-slate-500">
                  Used to sign payloads (HMAC SHA-256). Provide your own or generate a secure secret.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                  checked={formState.active}
                  onChange={(event) => setFormState((prev) => ({ ...prev, active: event.target.checked }))}
                />
                <span className="text-sm text-slate-700">Webhook is active</span>
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <Button variant="ghost" type="button" onClick={() => setIsModalOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={saveMutation.isLoading}>
                  {saveMutation.isLoading ? "Saving…" : editingWebhook ? "Save Changes" : "Create Webhook"}
                </Button>
              </div>
            </form>
          </Dialog.Panel>
        </div>
      </Dialog>
    </div>
  );
}

