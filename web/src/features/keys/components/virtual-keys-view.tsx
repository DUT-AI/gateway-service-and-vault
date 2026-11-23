"use client";

import React, { useState } from "react";
import { Key, Plus, Shield, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { VirtualKeysTable } from "./virtual-keys-table";
import { GenerateKeyModal } from "./generate-key-modal";

export interface VirtualKeysViewProps {
  projectId: string;
}

export function VirtualKeysView({ projectId }: VirtualKeysViewProps) {
  const [generateOpen, setGenerateOpen] = useState(false);

  return (
    <div className="space-y-4">
      {/* Container Card */}
      <Card className="border-slate-200 bg-white shadow-xs">
        <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-100 pb-4">
          <div className="space-y-1">
            <CardTitle className="text-base font-semibold text-slate-900 flex items-center gap-2">
              <Key className="h-4 w-4 text-emerald-600" />
              Virtual Keys & Zero-Trust Policies
              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-700 border border-emerald-200">
                <Shield className="h-2.5 w-2.5" />
                Principle VIII
              </span>
            </CardTitle>
            <p className="text-xs text-slate-500">
              Phát hành khóa ảo (Virtual Keys) cho phép ứng dụng truy xuất tài nguyên
              Gateway an toàn dưới cơ chế ràng buộc phần cứng 1:1.
            </p>
          </div>

          <Button
            type="button"
            size="sm"
            onClick={() => setGenerateOpen(true)}
            className="bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-xs h-9 px-3 shrink-0 shadow-xs"
          >
            <Plus className="h-3.5 w-3.5 mr-1" />
            Cấp Virtual Key mới
          </Button>
        </CardHeader>

        <CardContent className="pt-4">
          <VirtualKeysTable
            projectId={projectId}
            onGenerateClick={() => setGenerateOpen(true)}
          />
        </CardContent>
      </Card>

      {/* Generate Key Modal */}
      <GenerateKeyModal
        open={generateOpen}
        onOpenChange={setGenerateOpen}
        projectId={projectId}
      />
    </div>
  );
}
