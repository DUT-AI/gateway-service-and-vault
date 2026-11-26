"use client";

import React, { useState } from "react";
import {
  Check,
  Copy,
  Edit2,
  Eye,
  EyeOff,
  Lock,
  Plus,
  Trash2,
} from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { FlatSecretItem } from "../types";

export interface SecretsTableProps {
  items: FlatSecretItem[];
  isLoading: boolean;
  highlightedKeys?: Set<string>;
  onEditSecret?: (item: FlatSecretItem) => void;
  onDeleteSecret?: (item: FlatSecretItem) => void;
  onCreateSecret?: () => void;
}

export function SecretsTable({
  items,
  isLoading,
  highlightedKeys,
  onEditSecret,
  onDeleteSecret,
  onCreateSecret,
}: SecretsTableProps) {
  const [revealedKeys, setRevealedKeys] = useState<Set<string>>(new Set());
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const toggleReveal = (id: string) => {
    setRevealedKeys((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const copyToClipboard = async (item: FlatSecretItem) => {
    try {
      await navigator.clipboard.writeText(item.value);
      setCopiedId(item.id);
      toast.success(`Đã sao chép giá trị ${item.key} vào clipboard!`);
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      toast.error("Không thể sao chép giá trị");
    }
  };

  if (isLoading) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white overflow-hidden shadow-2xs">
        <Table>
          <TableHeader className="bg-slate-50/70">
            <TableRow>
              <TableHead className="w-[30%]">Key</TableHead>
              <TableHead className="w-[45%]">Giá trị (Decrypted)</TableHead>
              <TableHead className="w-[15%]">Nhóm (Scope)</TableHead>
              <TableHead className="w-[10%] text-right">Thao tác</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {Array.from({ length: 4 }).map((_, index) => (
              <TableRow key={index}>
                <TableCell>
                  <Skeleton className="h-4 w-32" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-4 w-48" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-5 w-20 rounded-full" />
                </TableCell>
                <TableCell className="text-right">
                  <Skeleton className="ml-auto h-7 w-14 rounded-md" />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="rounded-2xl border-2 border-dashed border-slate-200 bg-white p-10 text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-[#EEF3FA] text-[#042B5F] mb-3">
          <Lock className="h-6 w-6" />
        </div>
        <h3 className="text-sm font-semibold text-slate-900">
          Chưa có biến môi trường nào
        </h3>
        <p className="mt-1 text-xs text-slate-500 max-w-sm mx-auto leading-relaxed">
          Tạo biến môi trường đầu tiên để mã hóa an toàn qua AES-256-GCM và
          chia sẻ cấu hình không cần file .env.
        </p>
        {onCreateSecret && (
          <Button
            size="sm"
            onClick={onCreateSecret}
            className="mt-4 bg-[#042B5F] hover:bg-[#031F46] text-white font-medium"
          >
            <Plus className="h-3.5 w-3.5 mr-1" />
            Thêm biến mới
          </Button>
        )}
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white overflow-hidden shadow-2xs">
      <Table>
        <TableHeader className="bg-slate-50/70">
          <TableRow>
            <TableHead className="text-xs font-semibold text-slate-700 w-[30%]">
              Key
            </TableHead>
            <TableHead className="text-xs font-semibold text-slate-700 w-[45%]">
              Giá trị
            </TableHead>
            <TableHead className="text-xs font-semibold text-slate-700 w-[15%]">
              Nhóm (Scope)
            </TableHead>
            <TableHead className="text-xs font-semibold text-slate-700 w-[10%] text-right">
              Thao tác
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {items.map((item) => {
            const isRevealed = revealedKeys.has(item.id);
            const isCopied = copiedId === item.id;
            const isHighlighted = highlightedKeys?.has(item.key);

            return (
              <TableRow
                key={item.id}
                className={`transition-all duration-700 ${
                  isHighlighted
                    ? "bg-[#EEF3FA]/90 ring-2 ring-blue-500/50"
                    : "hover:bg-slate-50/60"
                }`}
              >
                <TableCell className="font-mono font-semibold text-xs text-slate-900">
                  <div className="flex items-center gap-2">
                    <span>{item.key}</span>
                    {isHighlighted && (
                      <span className="inline-flex items-center gap-1 rounded bg-[#EEF3FA] px-1.5 py-0.5 text-[10px] font-semibold text-[#042B5F] animate-pulse">
                        Vừa cập nhật
                      </span>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    {isRevealed ? (
                      <span className="font-mono text-xs text-slate-800 break-all bg-slate-50 px-2 py-0.5 rounded border border-slate-200 max-w-md">
                        {item.value}
                      </span>
                    ) : (
                      <span className="font-mono text-slate-400 select-none tracking-widest text-xs">
                        ••••••••••••••••
                      </span>
                    )}

                    <div className="flex items-center gap-1 shrink-0">
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon-sm"
                        onClick={() => toggleReveal(item.id)}
                        title={isRevealed ? "Ẩn giá trị" : "Hiện giá trị"}
                        className="h-7 w-7 text-slate-400 hover:text-slate-700"
                      >
                        {isRevealed ? (
                          <EyeOff className="h-3.5 w-3.5" />
                        ) : (
                          <Eye className="h-3.5 w-3.5" />
                        )}
                      </Button>

                      <Button
                        type="button"
                        variant="ghost"
                        size="icon-sm"
                        onClick={() => copyToClipboard(item)}
                        title="Sao chép giá trị"
                        className="h-7 w-7 text-slate-400 hover:text-slate-700"
                      >
                        {isCopied ? (
                          <Check className="h-3.5 w-3.5 text-emerald-600" />
                        ) : (
                          <Copy className="h-3.5 w-3.5" />
                        )}
                      </Button>
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <Badge
                    variant="outline"
                    className="font-mono text-[11px] bg-slate-50 text-slate-700 border-slate-200"
                  >
                    {item.scope_name}
                  </Badge>
                </TableCell>
                <TableCell className="text-right space-x-1">
                  {onEditSecret && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => onEditSecret(item)}
                      className="h-7 text-xs text-slate-600 hover:text-[#042B5F] hover:bg-[#EEF3FA] px-2.5"
                    >
                      <Edit2 className="h-3.5 w-3.5 mr-1" />
                      Sửa
                    </Button>
                  )}
                  {onDeleteSecret && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => onDeleteSecret(item)}
                      className="h-7 text-xs text-rose-600 hover:text-rose-700 hover:bg-rose-50 px-2.5"
                    >
                      <Trash2 className="h-3.5 w-3.5 mr-1" />
                      Xóa
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
