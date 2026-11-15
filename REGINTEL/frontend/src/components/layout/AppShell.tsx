import React, { useState, useEffect } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import type { BreadcrumbItem } from "./Breadcrumb";

const STORAGE_KEY = "tracecho_sidebar_collapsed";

export interface AppShellProps {
  breadcrumbs?: BreadcrumbItem[];
  children?: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ breadcrumbs, children }) => {
  const [collapsed, setCollapsed] = useState<boolean>(() => {
    try {
      return localStorage.getItem(STORAGE_KEY) === "true";
    } catch {
      return false;
    }
  });
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, String(collapsed));
    } catch {
      // ignore
    }
  }, [collapsed]);

  const toggleSidebar = () => {
    // On mobile, toggle drawer; on desktop, toggle collapse
    if (window.innerWidth < 768) {
      setMobileOpen((prev) => !prev);
    } else {
      setCollapsed((prev) => !prev);
    }
  };

  const closeMobile = () => setMobileOpen(false);

  return (
    <div className="flex h-screen overflow-hidden bg-bg-page font-sans text-text-main">
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/40 backdrop-blur-xs md:hidden"
          onClick={closeMobile}
        />
      )}

      {/* Sidebar container */}
      <div
        className={[
          "fixed md:static inset-y-0 left-0 z-50 flex-shrink-0 overflow-hidden",
          "transition-all duration-200 ease-in-out",
          // Mobile: slide in/out as drawer
          mobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0",
          // Desktop: width transition
          collapsed ? "md:w-[60px]" : "md:w-[240px]",
          "w-[240px]",
        ].join(" ")}
      >
        <Sidebar collapsed={collapsed} onClose={closeMobile} />
      </div>

      {/* Main content area */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <Topbar onToggleSidebar={toggleSidebar} breadcrumbs={breadcrumbs} />
        <main className="flex-1 overflow-y-auto p-6 bg-bg-page">
          {children ?? <Outlet />}
        </main>
      </div>
    </div>
  );
};

export default AppShell;
