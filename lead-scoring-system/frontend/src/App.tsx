import { LeadDashboard } from "./components/LeadDashboard";

function App() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white py-4 shadow-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6">
          <h1 className="text-2xl font-semibold">Lead Scoring Dashboard</h1>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8">
        <LeadDashboard />
      </main>
    </div>
  );
}

export default App;
