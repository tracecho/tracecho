import React from "react";
import { Menu, Search, Bell, User as UserIcon, LogOut, Settings } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { Breadcrumb, type BreadcrumbItem } from "./Breadcrumb";
import { Badge } from "@/components/ui/Badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/DropdownMenu";

export interface TopbarProps {
  onToggleSidebar?: () => void;
  breadcrumbs?: BreadcrumbItem[];
}

export const Topbar: React.FC<TopbarProps> = ({
  onToggleSidebar,
  breadcrumbs,
}) => {
  const { user, logout } = useAuth();

  const displayName = user?.name || user?.email?.split("@")[0] || "User";
  const userRole = (user as unknown as { role?: string })?.role || "Analyst";

  return (
    <header className="h-[56px] min-h-[56px] border-b border-border bg-white px-4 flex items-center justify-between select-none z-10">
      {/* Left section: toggle + breadcrumbs */}
      <div className="flex items-center space-x-3 min-w-0">
        <button
          onClick={onToggleSidebar}
          className="p-1.5 rounded-md text-text-muted hover:text-text-main hover:bg-bg-page transition-colors"
          aria-label="Toggle navigation"
        >
          <Menu className="h-5 w-5" />
        </button>

        {breadcrumbs && breadcrumbs.length > 0 && (
          <div className="hidden sm:block truncate">
            <Breadcrumb items={breadcrumbs} />
          </div>
        )}
      </div>

      {/* Right section: Search placeholder, Notifications, User Avatar */}
      <div className="flex items-center space-x-3">
        {/* Search icon (non-functional placeholder) */}
        <div
          className="flex items-center space-x-1.5 px-2.5 py-1.5 rounded-md text-xs text-text-muted bg-bg-page border border-border cursor-not-allowed opacity-60"
          title="Search placeholder (coming soon)"
        >
          <Search className="h-3.5 w-3.5" />
          <span className="hidden md:inline">Search...</span>
        </div>

        {/* Notification bell (non-functional) */}
        <button
          disabled
          className="p-1.5 rounded-md text-text-muted opacity-60 cursor-not-allowed"
          title="Notifications (coming soon)"
          aria-label="Notifications"
        >
          <Bell className="h-4 w-4" />
        </button>

        <div className="h-4 w-px bg-border" />

        {/* User Avatar Dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button
              className="flex items-center space-x-2 p-1 rounded-full hover:ring-2 hover:ring-primary/20 transition-all outline-none"
              aria-label="User menu"
            >
              <div className="h-8 w-8 rounded-full bg-primary/10 text-primary flex items-center justify-center font-semibold text-xs border border-primary/20">
                {displayName.charAt(0).toUpperCase()}
              </div>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel className="font-normal">
              <div className="flex flex-col space-y-1">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold text-text-main leading-none">
                    {displayName}
                  </p>
                  <Badge variant="default" className="text-[10px] px-1.5 py-0">
                    {userRole}
                  </Badge>
                </div>
                {user?.email && (
                  <p className="text-xs text-text-muted leading-none truncate">
                    {user.email}
                  </p>
                )}
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem disabled className="text-text-muted cursor-not-allowed">
              <Settings className="mr-2 h-4 w-4" />
              <span>Account Settings</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={logout}
              className="text-red-600 focus:text-red-600 focus:bg-red-50 cursor-pointer"
            >
              <LogOut className="mr-2 h-4 w-4" />
              <span>Sign out</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
};

export default Topbar;
