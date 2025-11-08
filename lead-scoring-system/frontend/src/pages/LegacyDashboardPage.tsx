import { DashboardLayout } from "../components/layout/DashboardLayout";
import { LeadDashboard } from "../components/LeadDashboard";

export function LegacyDashboardPage() {
  return (
    <DashboardLayout
      title="Lead Directory"
      subtitle="Browse every AI-scored lead across your organization"
    >
      <LeadDashboard />
    </DashboardLayout>
  );
}


