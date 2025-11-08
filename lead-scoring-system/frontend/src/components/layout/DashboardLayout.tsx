import { ReactNode, useState } from "react";

import { Sidebar } from "./Sidebar";
import { MobileMenu } from "./MobileMenu";
import { Header } from "./Header";

type DashboardLayoutProps = {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
  children: ReactNode;
};

export function DashboardLayout({ title, subtitle, actions, children }: DashboardLayoutProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-50">
      <Sidebar className="md:fixed md:inset-y-0 md:block md:w-72" />
      <MobileMenu open={mobileMenuOpen} onClose={() => setMobileMenuOpen(false)} />

      <div className="md:pl-72">
        <Header title={title} subtitle={subtitle} onToggleMenu={() => setMobileMenuOpen(true)} actions={actions} />
        <main className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          {children}
        </main>
      </div>
    </div>
  );
}


