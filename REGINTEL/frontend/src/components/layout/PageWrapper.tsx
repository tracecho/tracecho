import React from "react";
import { Breadcrumb, type BreadcrumbItem } from "./Breadcrumb";
import { cn } from "@/lib/utils";

export interface PageWrapperProps {
  title?: string;
  description?: string;
  breadcrumbs?: BreadcrumbItem[];
  actions?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export const PageWrapper: React.FC<PageWrapperProps> = ({
  title,
  description,
  breadcrumbs,
  actions,
  children,
  className,
}) => {
  return (
    <div className={cn("space-y-6 max-w-7xl mx-auto", className)}>
      {/* Top breadcrumb + header if specified */}
      {(title || breadcrumbs || actions) && (
        <div className="flex flex-col space-y-2 border-b border-border pb-4">
          {breadcrumbs && breadcrumbs.length > 0 && (
            <div className="mb-1">
              <Breadcrumb items={breadcrumbs} />
            </div>
          )}
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              {title && (
                <h1 className="text-2xl font-bold tracking-tight text-text-main">
                  {title}
                </h1>
              )}
              {description && (
                <p className="text-sm text-text-muted mt-1">{description}</p>
              )}
            </div>
            {actions && <div className="flex items-center space-x-3">{actions}</div>}
          </div>
        </div>
      )}

      {/* Page Content */}
      <div className="w-full">{children}</div>
    </div>
  );
};

export default PageWrapper;
