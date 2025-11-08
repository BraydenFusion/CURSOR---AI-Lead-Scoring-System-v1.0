import { ReactNode } from "react";
import { Menu } from "lucide-react";

import { NotificationBell } from "../NotificationBell";
import { useAuth } from "../../contexts/AuthContext";

type HeaderProps = {
  title: string;
  subtitle?: string;
  onToggleMenu?: () => void;
  actions?: ReactNode;
};

export function Header({ title, subtitle, onToggleMenu, actions }: HeaderProps) {
  const { user } = useAuth();

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-4">
          {onToggleMenu && (
            <button
              onClick={onToggleMenu}
              className="inline-flex items-center justify-center rounded-md border border-slate-200 bg-white p-2 text-slate-600 shadow-sm transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-navy-500 focus:ring-offset-2 md:hidden"
              aria-label="Open menu"
            >
              <Menu className="h-5 w-5" />
            </button>
          )}
          <div>
            <h1 className="text-lg font-semibold text-slate-900 sm:text-xl lg:text-2xl">{title}</h1>
            {subtitle ? (
              <p className="text-sm text-slate-500">{subtitle}</p>
            ) : user ? (
              <p className="text-sm text-slate-500">
                {user.full_name} • {user.role === "sales_rep" ? "Sales Representative" : user.role === "manager" ? "Sales Manager" : "System Admin"}
              </p>
            ) : null}
          </div>
        </div>
        <div className="flex items-center gap-3">
          <NotificationBell />
          {actions}
        </div>
      </div>
    </header>
  );
}


