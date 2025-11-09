import { Dialog } from "@headlessui/react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Copy, KeyRound, Lock, PlusCircle, ShieldCheck, Trash2 } from "lucide-react";
import { FormEvent, Fragment, useMemo, useState } from "react";
import { formatDistanceToNow } from "date-fns";

import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import {
  APIKey,
  APIKeyPermission,
  APIKeySecretResponse,
  APIKeyListResponse,
} from "../types";
import {
  createApiKey,
  deleteApiKey,
  fetchApiKeys,
  revokeApiKey,
} from "../services/developers";

type APIKeyFormState = {
  name: string;
  rate_limit: number;
  permissions: APIKeyPermission[];
};

const PERMISSION_LABELS: Record<APIKeyPermission, string> = {
  read_leads: "Read Leads",
  write_leads: "Write Leads",
  read_activities: "Read Activities",
  write_activities: "Write Activities",
  read_assignments: "Read Assignments",
  write_assignments: "Write Assignments",
};

export function APIKeysPage() {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formState, setFormState] = useState<APIKeyFormState>({
    name: "",
    rate_limit: 100,
    permissions: ["read_leads"],
  });
  const [createdKey, setCreatedKey] = useState<APIKeySecretResponse | null>(null);

  const apiKeysQuery = useQuery<APIKeyListResponse>({
    queryKey: ["apiKeys"],
    queryFn: fetchApiKeys,
  });

  const createMutation = useMutation({
    mutationFn: createApiKey,
    onSuccess: (data) => {
      setCreatedKey(data);
      setIsModalOpen(false);
      queryClient.invalidateQueries({ queryKey: ["apiKeys"] });
      setFormState({ name: "", rate_limit: 100, permissions: ["read_leads"] });
    },
  });

  const revokeMutation = useMutation({
    mutationFn: revokeApiKey,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["apiKeys"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteApiKey,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["apiKeys"] });
    },
  });

  const allPermissions = useMemo(() => Object.keys(PERMISSION_LABELS) as APIKeyPermission[], []);

  const handleTogglePermission = (permission: APIKeyPermission) => {
    setFormState((prev) => {
      const exists = prev.permissions.includes(permission);
      if (exists) {
        return { ...prev, permissions: prev.permissions.filter((perm) => perm !== permission) };
      }
      return { ...prev, permissions: [...prev.permissions, permission] };
    });
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!formState.name.trim()) return;
    createMutation.mutate({
      name: formState.name.trim(),
      rate_limit: formState.rate_limit,
      permissions: formState.permissions,
    });
  };

  const handleCopy = (value: string) => {
    navigator.clipboard.writeText(value).catch(() => {
      // eslint-disable-next-line no-console
      console.warn("Unable to copy API key to clipboard");
    });
  };

  const renderStatus = (key: APIKey) => {
    if (!key.active) {
      return <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-700">Revoked</span>;
    }
    return <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-700">Active</span>;
  };

  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">API Keys</h1>
          <p className="mt-1 text-sm text-slate-500">
            Securely manage access to the public API. Each key is rate limited and scoped to specific permissions.
          </p>
        </div>
        <Button onClick={() => setIsModalOpen(true)} className="inline-flex items-center gap-2">
          <PlusCircle className="h-4 w-4" />
          Create API Key
        </Button>
      </header>

      {createdKey && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="flex items-center gap-2 text-sm font-semibold text-amber-800">
                <Lock className="h-4 w-4" />
                API Key Generated
              </h2>
              <p className="mt-2 text-sm text-amber-700">
                Copy this key now. For security reasons it will not be shown again.
              </p>
              <pre className="mt-3 overflow-x-auto rounded-md bg-white px-3 py-2 text-sm text-slate-900 shadow-inner">{createdKey.api_key}</pre>
            </div>
            <Button variant="outline" onClick={() => handleCopy(createdKey.api_key)} className="mt-1 inline-flex items-center gap-2">
              <Copy className="h-4 w-4" />
              Copy
            </Button>
          </div>
        </div>
      )}

      <section className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Name
              </th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Key
              </th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Permissions
              </th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Rate Limit
              </th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Last Used
              </th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Status
              </th>
              <th scope="col" className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {apiKeysQuery.isLoading && (
              <tr>
                <td colSpan={7} className="px-4 py-6 text-center text-sm text-slate-500">
                  Loading API keys…
                </td>
              </tr>
            )}
            {apiKeysQuery.data?.items.length === 0 && !apiKeysQuery.isLoading && (
              <tr>
                <td colSpan={7} className="px-4 py-6 text-center text-sm text-slate-500">
                  No API keys yet. Create your first key to get started.
                </td>
              </tr>
            )}
            {apiKeysQuery.data?.items.map((key) => (
              <tr key={key.id}>
                <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-slate-900">{key.name}</td>
                <td className="px-4 py-3 text-sm text-slate-600">
                  <div className="flex items-center gap-2">
                    <KeyRound className="h-4 w-4 text-slate-400" />
                    <span>{key.key_preview}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-slate-600">
                  <div className="flex flex-wrap gap-2">
                    {key.permissions.map((perm) => (
                      <span key={perm} className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
                        <ShieldCheck className="h-3 w-3 text-slate-500" />
                        {PERMISSION_LABELS[perm]}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-600">{key.rate_limit.toLocaleString()} / hour</td>
                <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-600">
                  {key.last_used ? formatDistanceToNow(new Date(key.last_used), { addSuffix: true }) : "Never"}
                </td>
                <td className="px-4 py-3 text-sm">{renderStatus(key)}</td>
                <td className="whitespace-nowrap px-4 py-3 text-right text-sm">
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={!key.active || revokeMutation.isPending}
                      onClick={() => revokeMutation.mutate(key.id)}
                    >
                      Revoke
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-600 hover:bg-red-50 hover:text-red-700"
                      disabled={deleteMutation.isPending}
                      onClick={() => deleteMutation.mutate(key.id)}
                    >
                      <Trash2 className="mr-1 h-4 w-4" />
                      Delete
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <Dialog open={isModalOpen} onClose={() => setIsModalOpen(false)} as={Fragment}>
        <div className="fixed inset-0 z-30 flex items-center justify-center bg-slate-900/40 px-4 py-8">
          <Dialog.Panel className="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl">
            <Dialog.Title className="text-lg font-semibold text-slate-900">Create API Key</Dialog.Title>
            <form onSubmit={handleSubmit} className="mt-4 space-y-4">
              <div>
                <label className="text-sm font-medium text-slate-700">Key Name</label>
                <Input
                  value={formState.name}
                  onChange={(event) => setFormState((prev) => ({ ...prev, name: event.target.value }))}
                  placeholder="e.g. Website Integration"
                  required
                  className="mt-1"
                />
              </div>

              <div>
                <span className="text-sm font-medium text-slate-700">Permissions</span>
                <div className="mt-2 grid grid-cols-1 gap-2 md:grid-cols-2">
                  {allPermissions.map((permission) => (
                    <label
                      key={permission}
                      className="flex cursor-pointer items-center gap-2 rounded-md border border-slate-200 px-3 py-2 text-sm transition hover:border-slate-300"
                    >
                      <input
                        type="checkbox"
                        className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                        checked={formState.permissions.includes(permission)}
                        onChange={() => handleTogglePermission(permission)}
                      />
                      <span>{PERMISSION_LABELS[permission]}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-slate-700">Rate Limit (requests per hour)</label>
                <Input
                  type="number"
                  min={1}
                  max={10000}
                  value={formState.rate_limit}
                  onChange={(event) => setFormState((prev) => ({ ...prev, rate_limit: Number(event.target.value) }))}
                  className="mt-1"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <Button variant="ghost" type="button" onClick={() => setIsModalOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? "Creating…" : "Generate Key"}
                </Button>
              </div>
            </form>
          </Dialog.Panel>
        </div>
      </Dialog>
    </div>
  );
}

