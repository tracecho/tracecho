import React from "react";
import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

export interface BreadcrumbProps {
  items?: BreadcrumbItem[];
  className?: string;
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({ items = [], className }) => {
  if (!items || items.length === 0) return null;

  return (
    <nav aria-label="Breadcrumb" className={cn("flex items-center text-sm", className)}>
      <ol className="flex items-center space-x-1.5">
        {items.map((item, idx) => {
          const isLast = idx === items.length - 1;

          return (
            <li key={`${item.label}-${idx}`} className="flex items-center space-x-1.5">
              {idx > 0 && (
                <ChevronRight className="h-4 w-4 text-text-muted flex-shrink-0" />
              )}
              {item.href && !isLast ? (
                <Link
                  to={item.href}
                  className="text-text-muted hover:text-text-main transition-colors text-xs font-medium"
                >
                  {item.label}
                </Link>
              ) : (
                <span
                  className={cn(
                    "text-xs",
                    isLast
                      ? "text-text-main font-semibold"
                      : "text-text-muted font-medium"
                  )}
                  aria-current={isLast ? "page" : undefined}
                >
                  {item.label}
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

export default Breadcrumb;
