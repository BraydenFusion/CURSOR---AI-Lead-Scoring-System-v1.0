import { ExternalLink, FileCode2, Shield } from "lucide-react";

import { Button } from "../components/ui/button";

const pythonExample = `import requests

API_KEY = "your_api_key"
BASE_URL = "https://your-domain/api/v1"

headers = {"X-API-Key": API_KEY}

response = requests.get(f"{BASE_URL}/leads", params={"limit": 10}, headers=headers, timeout=10)
response.raise_for_status()
for lead in response.json()["items"]:
    print(lead["name"], lead["current_score"])
`;

const javascriptExample = `const apiKey = "your_api_key";
const baseUrl = "https://your-domain/api/v1";

async function listLeads() {
  const response = await fetch(\`\${baseUrl}/leads?limit=10\`, {
    headers: {
      "X-API-Key": apiKey,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(\`API request failed: \${response.status}\`);
  }

  const payload = await response.json();
  console.log(payload.items);
}

listLeads().catch(console.error);
`;

const curlExample = `curl -X POST https://your-domain/api/v1/leads \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your_api_key" \\
  -d '{
    "name": "Acme Corp",
    "email": "sales@acme.com",
    "source": "web_form",
    "metadata": {"campaign": "winter-ads"}
  }'
`;

export function APIDocsPage() {
  return (
    <div className="space-y-6">
      <header className="flex flex-col items-start gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Public API Documentation</h1>
          <p className="mt-1 max-w-3xl text-sm text-slate-500">
            Integrate the Lead Scoring System into your product or automation workflows. Authenticate using the{" "}
            <span className="font-medium text-slate-700">X-API-Key</span> header. All endpoints are available via HTTPS only.
          </p>
        </div>
        <Button
          className="inline-flex items-center gap-2"
          onClick={() => window.open("/api/v1/docs", "_blank", "noopener")}
        >
          <ExternalLink className="h-4 w-4" />
          Open Swagger UI
        </Button>
      </header>

      <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <article className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="flex items-center gap-2 text-sm font-semibold text-slate-900">
            <Shield className="h-4 w-4 text-blue-600" />
            Authentication
          </h2>
          <ul className="mt-3 space-y-2 text-sm text-slate-600">
            <li>• Provide your API key using the <code className="rounded bg-slate-100 px-1 py-0.5 text-xs">X-API-Key</code> header.</li>
            <li>• Keys can be scoped to granular permissions (read/write leads, activities, assignments).</li>
            <li>• Rate limit defaults to 100 requests/hour and can be customized per key.</li>
            <li>• Responses include <code className="rounded bg-slate-100 px-1 py-0.5 text-xs">X-RateLimit-Remaining</code> and <code className="rounded bg-slate-100 px-1 py-0.5 text-xs">X-RateLimit-Reset</code> headers.</li>
          </ul>
        </article>

        <article className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm lg:col-span-2">
          <h2 className="text-sm font-semibold text-slate-900">Available Webhook Events</h2>
          <div className="mt-3 grid grid-cols-1 gap-2 text-sm text-slate-600 md:grid-cols-2">
            <span className="rounded-md border border-slate-200 px-3 py-2">lead.created – Triggered when a new lead is created</span>
            <span className="rounded-md border border-slate-200 px-3 py-2">lead.updated – Fired when a lead is updated</span>
            <span className="rounded-md border border-slate-200 px-3 py-2">lead.scored – Fired after scoring is recalculated</span>
            <span className="rounded-md border border-slate-200 px-3 py-2">lead.assigned – When a lead owner is assigned</span>
            <span className="rounded-md border border-slate-200 px-3 py-2">lead.converted – Triggered on conversion to customer</span>
            <span className="rounded-md border border-slate-200 px-3 py-2">note.added – When a note is added to a lead</span>
            <span className="rounded-md border border-slate-200 px-3 py-2">activity.created – When a new activity is logged</span>
          </div>
        </article>
      </section>

      <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <article className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="flex items-center gap-2 text-sm font-semibold text-slate-900">
            <FileCode2 className="h-4 w-4 text-indigo-600" />
            Python
          </h2>
          <pre className="mt-3 max-h-[260px] overflow-auto rounded-md bg-slate-900 px-4 py-3 text-xs text-slate-100">
            {pythonExample}
          </pre>
        </article>

        <article className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="flex items-center gap-2 text-sm font-semibold text-slate-900">
            <FileCode2 className="h-4 w-4 text-indigo-600" />
            JavaScript (fetch)
          </h2>
          <pre className="mt-3 max-h-[260px] overflow-auto rounded-md bg-slate-900 px-4 py-3 text-xs text-slate-100">
            {javascriptExample}
          </pre>
        </article>

        <article className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="flex items-center gap-2 text-sm font-semibold text-slate-900">
            <FileCode2 className="h-4 w-4 text-indigo-600" />
            cURL
          </h2>
          <pre className="mt-3 max-h-[260px] overflow-auto rounded-md bg-slate-900 px-4 py-3 text-xs text-slate-100">
            {curlExample}
          </pre>
        </article>
      </section>
    </div>
  );
}

