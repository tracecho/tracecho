import React from "react";
import { NavLink } from "react-router-dom";
import {
  ShieldCheck,
  LayoutDashboard,
  MessageSquare,
  FileSearch,
  BarChart2,
  LogOut,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { Badge } from "@/components/ui/Badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/Tooltip";

interface SidebarProps {
  collapsed: boolean;
  onClose?: () => void;
}

interface NavItem {
  name: string;
  to: string;
  icon: React.ElementType;
}

const navItems: NavItem[] = [
  { name: "Dashboard", to: "/app", icon: LayoutDashboard },
  { name: "AI Assistant", to: "/app/assistant", icon: MessageSquare },
  { name: "Document Explorer", to: "/app/explorer", icon: FileSearch },
  { name: "Evaluation", to: "/app/evaluation", icon: BarChart2 },
];

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onClose }) => {
  const { user, logout } = useAuth();

  const displayName = user?.name || user?.email?.split("@")[0] || "User";
  const userRole = (user as unknown as { role?: string })?.role || "Analyst";

  return (
    <TooltipProvider delayDuration={150}>
      <aside
        className={cn(
          "flex flex-col h-full bg-surface border-r border-border select-none transition-all duration-200",
          collapsed ? "w-[60px]" : "w-[240px]"
        )}
      >
        {/* Brand / Logo Header */}
        <div className="flex items-center justify-between h-[56px] px-3.5 border-b border-border">
          <div className="flex items-center space-x-2.5 overflow-hidden">
            <div className="flex items-center justify-center h-8 w-8 rounded-md bg-primary text-white flex-shrink-0">
              <ShieldCheck className="h-5 w-5" />
            </div>
            {!collapsed && (
              <span className="font-bold text-base tracking-wider text-text-main truncate">
                TRACECHO
              </span>
            )}
          </div>
          {/* Mobile close button */}
          {onClose && (
            <button
              onClick={onClose}
              className="p-1 rounded-md text-text-muted hover:text-text-main hover:bg-bg-page md:hidden"
              aria-label="Close sidebar"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 py-4 px-2 space-y-1.5 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;

            const linkContent = (
              <NavLink
                to={item.to}
                end={item.to === "/app"}
                onClick={() => onClose?.()}
                className={({ isActive }) =>
                  cn(
                    "flex items-center rounded-md text-sm font-medium transition-colors relative group",
                    collapsed
                      ? "justify-center h-10 w-10 mx-auto"
                      : "px-3 py-2.5 space-x-3 w-full",
                    isActive
                      ? "bg-primary/10 text-primary font-semibold border-l-[3px] border-primary"
                      : "text-text-muted hover:text-text-main hover:bg-bg-page"
                  )
                }
              >
                <Icon className="h-4 w-4 flex-shrink-0" />
                {!collapsed && <span className="truncate">{item.name}</span>}
              </NavLink>
            );

            if (collapsed) {
              return (
                <Tooltip key={item.to}>
                  <TooltipTrigger asChild>
                    <div>{linkContent}</div>
                  </TooltipTrigger>
                  <TooltipContent side="right" className="font-medium">
                    {item.name}
                  </TooltipContent>
                </Tooltip>
              );
            }

            return <div key={item.to}>{linkContent}</div>;
          })}
        </nav>

        {/* Bottom User Profile Section */}
        <div className="p-2 border-t border-border">
          {collapsed ? (
            <div className="flex flex-col items-center space-y-2">
              <Tooltip>
                <TooltipTrigger asChild>
                  <div className="h-8 w-8 rounded-full bg-primary/10 text-primary flex items-center justify-center font-semibold text-xs cursor-default">
                    {displayName.charAt(0).toUpperCase()}
                  </div>
                </TooltipTrigger>
                <TooltipContent side="right">
                  <p className="font-medium">{displayName}</p>
                  <p className="text-[10px] text-zinc-300 capitalize">{userRole}</p>
                </TooltipContent>
              </Tooltip>

              <Tooltip>
                <TooltipTrigger asChild>
                  <button
                    onClick={logout}
                    className="h-8 w-8 rounded-md flex items-center justify-center text-text-muted hover:text-red-600 hover:bg-red-50 transition-colors"
                    aria-label="Sign out"
                  >
                    <LogOut className="h-4 w-4" />
                  </button>
                </TooltipTrigger>
                <TooltipContent side="right">Sign out</TooltipContent>
              </Tooltip>
            </div>
          ) : (
            <div className="flex items-center justify-between p-2 rounded-lg bg-bg-page/60 border border-border/50">
              <div className="flex items-center space-x-2.5 min-w-0">
                <div className="h-8 w-8 rounded-full bg-primary/10 text-primary flex items-center justify-center font-semibold text-xs flex-shrink-0">
                  {displayName.charAt(0).toUpperCase()}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center space-x-1.5">
                    <p className="text-xs font-semibold text-text-main truncate">
                      {displayName}
                    </p>
                    <Badge variant="default" className="text-[10px] px-1.5 py-0">
                      {userRole}
                    </Badge>
                  </div>
                  {user?.email && (
                    <p className="text-[11px] text-text-muted truncate">
                      {user.email}
                    </p>
                  )}
                </div>
              </div>
              <button
                onClick={logout}
                className="p-1.5 rounded-md text-text-muted hover:text-red-600 hover:bg-red-50 transition-colors flex-shrink-0"
                title="Sign out"
                aria-label="Sign out"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>
      </aside>
    </TooltipProvider>
  );
};

export default Sidebar;
