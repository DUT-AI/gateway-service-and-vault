"use client";

import React from "react";
import { FolderLock } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { Scope } from "../types";

export interface ScopeTabsProps {
  scopes: Scope[];
  selectedScope: string;
  onSelectScope: (scope: string) => void;
  scopeCounts?: Record<string, number>;
  totalCount: number;
}

export function ScopeTabs({
  scopes,
  selectedScope,
  onSelectScope,
  scopeCounts = {},
  totalCount,
}: ScopeTabsProps) {
  return (
    <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
      <button
        type="button"
        onClick={() => onSelectScope("ALL")}
        className={`inline-flex cursor-pointer items-center gap-2 rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
          selectedScope === "ALL"
            ? "border border-blue-200 bg-blue-50 text-blue-700 shadow-2xs"
            : "border border-transparent text-slate-600 hover:bg-slate-100 hover:text-slate-900"
        }`}
      >
        <span>Tất cả</span>
        <Badge
          variant="secondary"
          className={`h-4.5 px-1.5 text-[10px] ${
            selectedScope === "ALL"
              ? "bg-blue-100 text-blue-800"
              : "bg-slate-200 text-slate-700"
          }`}
        >
          {totalCount}
        </Badge>
      </button>

      {scopes.map((scope) => {
        const count = scopeCounts[scope.name] ?? 0;
        const isSelected = selectedScope === scope.name;

        return (
          <button
            key={scope.id}
            type="button"
            onClick={() => onSelectScope(scope.name)}
            className={`inline-flex cursor-pointer items-center gap-2 rounded-lg px-3 py-1.5 text-xs font-semibold whitespace-nowrap transition-all ${
              isSelected
                ? "border border-blue-200 bg-blue-50 text-blue-700 shadow-2xs"
                : "border border-transparent text-slate-600 hover:bg-slate-100 hover:text-slate-900"
            }`}
          >
            <FolderLock
              className={`h-3.5 w-3.5 ${
                isSelected ? "text-blue-600" : "text-slate-400"
              }`}
            />
            <span>{scope.name}</span>
            <Badge
              variant="secondary"
              className={`h-4.5 px-1.5 text-[10px] ${
                isSelected
                  ? "bg-blue-100 text-blue-800"
                  : "bg-slate-200 text-slate-700"
              }`}
            >
              {count}
            </Badge>
          </button>
        );
      })}
    </div>
  );
}
