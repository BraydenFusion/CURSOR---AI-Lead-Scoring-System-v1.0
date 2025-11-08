import { Fragment } from "react";
import { Dialog, Transition } from "@headlessui/react";
import {
  LayoutDashboard,
  Users,
  Briefcase,
  ClipboardList,
  Settings,
  BarChart3,
  TrendingUp,
  FileText,
  Home,
  LogOut,
  Workflow,
} from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

type MobileMenuProps = {
  open: boolean;
  onClose: () => void;
};

type MenuItem = {
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

export function MobileMenu({ open, onClose }: MobileMenuProps) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const menuItems: MenuItem[] = [
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
      label: "Assignment Rules",
      icon: Workflow,
      to: "/assignment-rules",
      roles: ["manager", "admin"] as Array<"admin" | "manager" | "sales_rep">,
    },
    {
      label: "Reports",
      icon: FileText,
      to: "/dashboard/reports",
      roles: ["manager", "admin"] as Array<"admin" | "manager" | "sales_rep">,
    },
    {
      label: "Administration",
      icon: Users,
      to: "/dashboard/owner",
      roles: ["admin"] as Array<"admin" | "manager" | "sales_rep">,
    },
    { label: "Settings", icon: Settings, to: "/settings" },
    { label: "Marketing Site", icon: Home, to: "/" },
  ].filter((item) => {
    if (!item.roles) return true;
    if (!user?.role) return false;
    return item.roles.includes(user.role);
  });

  const handleNavigate = (path: string) => {
    navigate(path);
    onClose();
  };

  return (
    <Transition show={open} as={Fragment}>
      <Dialog as="div" className="relative z-40 md:hidden" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-in-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in-out duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-slate-900/25" />
        </Transition.Child>

        <div className="fixed inset-0 flex">
          <Transition.Child
            as={Fragment}
            enter="transform transition ease-in-out duration-300"
            enterFrom="-translate-x-full"
            enterTo="translate-x-0"
            leave="transform transition ease-in-out duration-200"
            leaveFrom="translate-x-0"
            leaveTo="-translate-x-full"
          >
            <Dialog.Panel className="relative flex w-full max-w-xs flex-1 flex-col bg-white">
              <div className="flex h-16 items-center justify-between border-b border-slate-200 px-4">
                <div>
                  <Dialog.Title className="text-lg font-semibold text-slate-900">LeadScore AI</Dialog.Title>
                  <p className="text-xs text-slate-500">Prioritize every lead</p>
                </div>
              </div>
              <div className="flex-1 overflow-y-auto px-3 py-6">
                <nav className="space-y-1">
                  {menuItems.map((item) => {
                    const isActive = location.pathname.startsWith(item.to);
                    const Icon = item.icon;
                    return (
                      <button
                        key={item.to}
                        onClick={() => handleNavigate(item.to)}
                        className={`flex w-full items-center gap-3 rounded-md px-3 py-2 text-left text-sm font-medium ${
                          isActive
                            ? "bg-navy-50 text-navy-700"
                            : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                        }`}
                      >
                        <Icon className="h-4 w-4" />
                        <span>{item.label}</span>
                      </button>
                    );
                  })}
                </nav>
              </div>
              <div className="border-t border-slate-200 px-4 py-4">
                {user && (
                  <div className="mb-3 rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm">
                    <p className="font-medium text-slate-900">{user.full_name}</p>
                    <p className="text-xs capitalize text-slate-500">{user.role.replace("_", " ")}</p>
                  </div>
                )}
                <button
                  onClick={() => {
                    logout();
                    onClose();
                  }}
                  className="flex w-full items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
                >
                  <LogOut className="h-4 w-4" />
                  Logout
                </button>
              </div>
            </Dialog.Panel>
          </Transition.Child>
          <div className="w-14 flex-shrink-0" aria-hidden="true" />
        </div>
      </Dialog>
    </Transition>
  );
}


