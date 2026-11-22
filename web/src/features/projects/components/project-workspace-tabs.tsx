"use client";

import React from "react";
import {
  Key,
  Lock,
  Settings,
  Sparkles,
  ShieldAlert,
  ArrowRight,
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { Project } from "../types";

export interface ProjectWorkspaceTabsProps {
  project: Project;
}

export function ProjectWorkspaceTabs({ project }: ProjectWorkspaceTabsProps) {
  return (
    <Tabs defaultValue="vault" className="space-y-6">
      <TabsList className="bg-slate-100 p-1 rounded-xl border border-slate-200">
        <TabsTrigger
          value="vault"
          className="rounded-lg text-xs font-semibold data-active:bg-white data-active:text-blue-700 data-active:shadow-xs px-4 py-2"
        >
          <Lock className="h-4 w-4 mr-2 text-slate-500" />
          Biến môi trường (Vault)
        </TabsTrigger>
        <TabsTrigger
          value="keys"
          className="rounded-lg text-xs font-semibold data-active:bg-white data-active:text-blue-700 data-active:shadow-xs px-4 py-2"
        >
          <Key className="h-4 w-4 mr-2 text-slate-500" />
          Virtual Keys
        </TabsTrigger>
        <TabsTrigger
          value="settings"
          className="rounded-lg text-xs font-semibold data-active:bg-white data-active:text-blue-700 data-active:shadow-xs px-4 py-2"
        >
          <Settings className="h-4 w-4 mr-2 text-slate-500" />
          Cài đặt dự án
        </TabsTrigger>
      </TabsList>

      {/* Vault Tab (Phase 2 Preview) */}
      <TabsContent value="vault" className="space-y-4">
        <Card className="border-slate-200 bg-white">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-base font-semibold text-slate-900 flex items-center gap-2">
                  <Lock className="h-4 w-4 text-blue-600" />
                  Dynamic Vault Engine
                </CardTitle>
                <p className="text-xs text-slate-500 mt-1">
                  Mã hóa và quản trị các biến môi trường bảo mật (Environment Secrets) cho không gian làm việc{" "}
                  <span className="font-semibold text-slate-700">{project.name}</span>.
                </p>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50/70 p-8 text-center space-y-3">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-blue-100 text-blue-700">
                <Sparkles className="h-6 w-6" />
              </div>
              <h4 className="text-sm font-semibold text-slate-800">
                Sẵn sàng cho Giai đoạn 2 (Dynamic Vault Engine)
              </h4>
              <p className="text-xs text-slate-500 max-w-md mx-auto leading-relaxed">
                Tại đây bạn sẽ tạo các Secret Key, phân loại theo môi trường
                (Development, Staging, Production) và cấu hình mã hóa tự động
                Zero-Knowledge.
              </p>
            </div>
          </CardContent>
        </Card>
      </TabsContent>

      {/* Virtual Keys Tab (Phase 3 Preview) */}
      <TabsContent value="keys" className="space-y-4">
        <Card className="border-slate-200 bg-white">
          <CardHeader>
            <CardTitle className="text-base font-semibold text-slate-900 flex items-center gap-2">
              <Key className="h-4 w-4 text-emerald-600" />
              Virtual Keys & Zero-Trust Policies
            </CardTitle>
            <p className="text-xs text-slate-500 mt-1">
              Phát hành và quản lý khóa ảo (Virtual Keys) cho phép ứng dụng client truy xuất tài nguyên gateway an toàn.
            </p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50/70 p-8 text-center space-y-3">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700">
                <Key className="h-6 w-6" />
              </div>
              <h4 className="text-sm font-semibold text-slate-800">
                Sẵn sàng cho Giai đoạn 3 (Virtual Keys)
              </h4>
              <p className="text-xs text-slate-500 max-w-md mx-auto leading-relaxed">
                Quản lý vòng đời khóa ảo, thiết lập thời gian sống (TTL), giới hạn
                hạn mức lưu lượng (Rate Limit) và danh sách địa chỉ IP hợp lệ.
              </p>
            </div>
          </CardContent>
        </Card>
      </TabsContent>

      {/* Settings Tab */}
      <TabsContent value="settings" className="space-y-4">
        <Card className="border-slate-200 bg-white">
          <CardHeader>
            <CardTitle className="text-base font-semibold text-slate-900">
              Thông tin cấu hình dự án
            </CardTitle>
            <p className="text-xs text-slate-500">
              Các thông số nhận diện dự án trong hệ thống DUT-AI Platform.
            </p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 text-xs">
              <div className="rounded-lg border border-slate-200 p-3 bg-slate-50/50">
                <p className="text-slate-500 font-medium">Mã định danh hệ thống (ID)</p>
                <p className="font-mono font-semibold text-slate-800 mt-1">
                  {project.id}
                </p>
              </div>
              <div className="rounded-lg border border-slate-200 p-3 bg-slate-50/50">
                <p className="text-slate-500 font-medium">Mã URL (Slug)</p>
                <p className="font-mono font-semibold text-slate-800 mt-1">
                  {project.slug}
                </p>
              </div>
              <div className="rounded-lg border border-slate-200 p-3 bg-slate-50/50 sm:col-span-2">
                <p className="text-slate-500 font-medium">Thời gian tạo</p>
                <p className="font-semibold text-slate-800 mt-1">
                  {new Date(project.created_at).toLocaleString("vi-VN")}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  );
}
