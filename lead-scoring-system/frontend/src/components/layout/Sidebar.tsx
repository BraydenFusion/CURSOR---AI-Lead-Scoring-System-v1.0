import { useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  Briefcase,
  ClipboardList,
  Settings,
  BarChart3,
  TrendingUp,
  Home,
} from "lucide-react";
import clsx from "clsx";

import { useAuth } from "../../contexts/AuthContext";
import { Button } from "../ui/button";

type SidebarProps = {
  onNavigate?: () => void;
  className?: string;
};

type NavItem = {
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  to: string;
  roles?: Array<"admin" | "manager" | "sales_rep">;
};

function getDashboardPath(role: "admin" | "manager" | "sales_rep" | undefined) {
  if (role === "admin") return "/dashboard/owner";
  if (role === "manager") return "/dashboard/manager";
  if (role === "sales_rep") return "/dashboard/sales-rep";
  return "/dashboard";
}

export function Sidebar({ onNavigate, className }: SidebarProps) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const navItems = useMemo<NavItem[]>(() => {
    const items: NavItem[] = [
      { label: "Dashboard", icon: LayoutDashboard, to: getDashboardPath(user?.role) },
      {
        label: "My Leads",
        icon: ClipboardList,
        to: "/my-leads",
        roles: ["sales_rep", "manager", "admin"] as Array<"admin" | "manager" | "sales_rep">,
      },
      { label: "Lead Directory", icon: Briefcase, to: "/dashboard/legacy" },
      {
        label: "Team Performance",
        icon: BarChart3,
        to: "/dashboard/manager",
        roles: ["manager", "admin"] as Array<"admin" | "manager" | "sales_rep">,
      },
      {
        label: "Analytics",
        icon: TrendingUp,
        to: "/dashboard/analytics",
        roles: ["manager", "admin"] as Array<"admin" | "manager" | "sales_rep">,
      },
      {
        label: "Administration",
        icon: Users,
        to: "/dashboard/owner",
        roles: ["admin"] as Array<"admin" | "manager" | "sales_rep">,
      },
      { label: "Settings", icon: Settings, to: "/settings" },
    ];

    // Marketing site quick link
    items.push({ label: "Marketing Site", icon: Home, to: "/" });

    return items.filter((item) => {
      if (!item.roles) return true;
      if (!user?.role) return false;
      return item.roles.includes(user.role);
    });
  }, [user?.role]);

  const handleNavigate = (path: string) => {
    navigate(path);
    onNavigate?.();
  };

  return (
    <aside
      className={clsx(
        "hidden w-72 flex-shrink-0 border-r border-slate-200 bg-white md:flex md:flex-col",
        className,
      )}
    >
      <div className="flex h-16 items-center justify-between border-b border-slate-200 px-6">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">LeadScore AI</h2>
          <p className="text-xs text-slate-500">Prioritize every lead</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-4 py-6">
        {navItems.map((item) => {
          const isActive = location.pathname.startsWith(item.to);
          const Icon = item.icon;
          return (
            <button
              key={item.to}
              onClick={() => handleNavigate(item.to)}
              className={clsx(
                "flex w-full items-center gap-3 rounded-md px-3 py-2 text-left text-sm font-medium transition",
                isActive
                  ? "bg-navy-50 text-navy-700"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
              )}
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="border-t border-slate-200 px-4 py-4">
        {user && (
          <div className="mb-3 rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm">
            <p className="font-medium text-slate-900">{user.full_name}</p>
            <p className="text-xs capitalize text-slate-500">{user.role.replace("_", " ")}</p>
          </div>
        )}
        <Button variant="outline" className="w-full" onClick={logout}>
          Logout
        </Button>
      </div>
    </aside>
  );
}


