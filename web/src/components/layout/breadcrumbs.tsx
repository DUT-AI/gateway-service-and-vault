"use client";

import React from "react";
import Link from "next/link";
import { ChevronRight, Home } from "lucide-react";

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

export interface BreadcrumbsProps {
  items: BreadcrumbItem[];
  className?: string;
}

export function Breadcrumbs({ items, className = "" }: BreadcrumbsProps) {
  return (
    <nav
      aria-label="Breadcrumb"
      className={`flex items-center text-xs text-slate-500 ${className}`}
    >
      <ol className="flex items-center space-x-1.5 flex-wrap">
        <li className="inline-flex items-center">
          <Link
            href="/dashboard"
            className="inline-flex items-center text-slate-400 hover:text-slate-700 transition-colors"
          >
            <Home className="h-3.5 w-3.5 mr-1" />
            <span>Trang chủ</span>
          </Link>
        </li>
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          return (
            <li key={index} className="inline-flex items-center">
              <ChevronRight className="h-3 w-3 text-slate-400 mx-1 shrink-0" />
              {item.href && !isLast ? (
                <Link
                  href={item.href}
                  className="font-medium text-slate-600 hover:text-[#042B5F] transition-colors truncate max-w-[200px]"
                >
                  {item.label}
                </Link>
              ) : (
                <span
                  className="font-semibold text-slate-900 truncate max-w-[260px]"
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
}
