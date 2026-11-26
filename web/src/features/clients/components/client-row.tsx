"use client";

import React from "react";
import Image from "next/image";
import { Ban, Calendar, Check, Copy, Laptop, Server } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Client } from "../types";

export interface ClientOwnerInfo {
  name: string;
  email?: string;
  avatar_url?: string | null;
}

export interface ClientRowProps {
  client: Client;
  owner?: ClientOwnerInfo;
  isCopied: boolean;
  onCopyFingerprint: (clientId: string, fingerprint: string) => void;
  onRevokeClick: (client: Client) => void;
}

function getClientStatus(client: Client) {
  if (client.is_revoked) {
    return {
      label: "Đã thu hồi",
      variant: "destructive" as const,
      className: "bg-rose-50 text-rose-700 border-rose-200",
    };
  }
  const isExpired = new Date(client.expires_at).getTime() < Date.now();
  if (isExpired) {
    return {
      label: "Hết hạn",
      variant: "outline" as const,
      className: "bg-amber-50 text-amber-700 border-amber-200",
    };
  }
  return {
    label: "Đang hoạt động",
    variant: "outline" as const,
    className: "bg-emerald-50 text-emerald-700 border-emerald-200",
  };
}

export function ClientRow({
  client,
  owner,
  isCopied,
  onCopyFingerprint,
  onRevokeClick,
}: ClientRowProps) {
  const status = getClientStatus(client);
  const isDeveloper = client.client_type === "USER_DEVICE";

  return (
    <tr className="hover:bg-slate-50/70 transition-colors">
      <td className="py-3 px-4">
        <div className="flex items-center gap-2.5">
          <div
            className={`h-8 w-8 rounded-lg flex items-center justify-center shrink-0 ${
              isDeveloper
                ? "bg-[#EEF3FA] text-[#042B5F]"
                : "bg-purple-50 text-purple-600"
            }`}
          >
            {isDeveloper ? (
              <Laptop className="h-4 w-4" />
            ) : (
              <Server className="h-4 w-4" />
            )}
          </div>
          <div className="truncate max-w-[200px] sm:max-w-xs">
            <div className="font-semibold text-slate-900 truncate">
              {client.name}
            </div>
            <div className="text-[10px] text-slate-400 font-mono">
              SN: {client.cert_serial.slice(0, 12)}...
            </div>
          </div>
        </div>
      </td>

      <td className="py-3 px-4">
        <div className="flex items-center gap-2 min-w-0">
          {owner?.avatar_url ? (
            <Image
              src={owner.avatar_url}
              alt={owner.name}
              width={24}
              height={24}
              className="h-6 w-6 rounded-full object-cover border border-slate-200 shrink-0"
            />
          ) : (
            <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-100 text-[10px] font-bold text-slate-600">
              {(owner?.name || client.owner_id || "U")[0].toUpperCase()}
            </div>
          )}
          <div className="min-w-0 max-w-[160px]">
            <div className="font-medium text-slate-800 truncate">
              {owner?.name || `User #${client.owner_id}`}
            </div>
            {owner?.email && (
              <div className="text-[10px] text-slate-400 truncate">
                {owner.email}
              </div>
            )}
          </div>
        </div>
      </td>

      <td className="py-3 px-4">
        <Badge
          variant="outline"
          className={`text-[10px] font-semibold border ${
            isDeveloper
              ? "bg-[#EEF3FA] text-[#042B5F] border-[#042B5F]/20"
              : "bg-purple-50 text-purple-700 border-purple-200"
          }`}
        >
          {isDeveloper ? "Developer PC" : "Workload Server"}
        </Badge>
      </td>

      <td className="py-3 px-4">
        <div className="inline-flex items-center gap-1.5 bg-slate-100/80 px-2 py-1 rounded-md border border-slate-200 font-mono text-[11px] text-slate-700">
          <span className="truncate max-w-[140px] sm:max-w-[180px]">
            {client.cert_fingerprint.slice(0, 16)}...
            {client.cert_fingerprint.slice(-8)}
          </span>
          <button
            type="button"
            onClick={() =>
              onCopyFingerprint(client.id, client.cert_fingerprint)
            }
            className="text-slate-400 hover:text-slate-700 transition-colors p-0.5"
            title="Sao chép toàn bộ Fingerprint"
          >
            {isCopied ? (
              <Check className="h-3 w-3 text-emerald-600" />
            ) : (
              <Copy className="h-3 w-3" />
            )}
          </button>
        </div>
      </td>

      <td className="py-3 px-4 text-slate-600">
        <div className="flex items-center gap-1.5">
          <Calendar className="h-3.5 w-3.5 text-slate-400 shrink-0" />
          <span>{new Date(client.expires_at).toLocaleDateString("vi-VN")}</span>
        </div>
      </td>

      <td className="py-3 px-4 text-center">
        <Badge
          variant={status.variant}
          className={`text-[10px] font-semibold border ${status.className}`}
        >
          {status.label}
        </Badge>
      </td>

      <td className="py-3 px-4 text-right">
        {client.is_revoked ? (
          <span className="text-[11px] text-slate-400 font-medium">
            Đã thu hồi
          </span>
        ) : (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => onRevokeClick(client)}
            className="h-7 text-xs text-rose-600 hover:text-rose-700 hover:bg-rose-50 px-2"
            title="Thu hồi thiết bị và tất cả Virtual Keys liên kết"
          >
            <Ban className="h-3 w-3 mr-1" />
            Thu hồi
          </Button>
        )}
      </td>
    </tr>
  );
}
