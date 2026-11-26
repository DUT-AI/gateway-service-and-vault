"use client";

import React from "react";
import {
  Key,
  Lock,
  Server,
  Settings,
  Users,
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/contexts/auth-context";
import { VaultView } from "@/features/vault";
import { VirtualKeysView } from "@/features/keys";
import { ProjectAllowedServicesView } from "./project-allowed-services-view";
import { ProjectMembersView } from "./project-members-view";
import type { Project } from "../types";

export interface ProjectWorkspaceTabsProps {
  project: Project;
}

export function ProjectWorkspaceTabs({ project }: ProjectWorkspaceTabsProps) {
  const { isAdmin, isDeveloper } = useAuth();
  const canManageKeys = isAdmin || isDeveloper;

  return (
    <Tabs defaultValue="vault" className="space-y-6">
      <TabsList className="bg-white p-1 rounded-xl border border-slate-200/80 shadow-2xs">
        <TabsTrigger
          value="vault"
          className="rounded-lg text-xs font-semibold text-slate-600 data-active:bg-[#042B5F] data-active:text-white data-active:shadow-xs px-4 py-2"
        >
          <Lock className="h-4 w-4 mr-2" />
          Biến môi trường (Vault)
        </TabsTrigger>
        <TabsTrigger
          value="keys"
          className="rounded-lg text-xs font-semibold text-slate-600 data-active:bg-[#042B5F] data-active:text-white data-active:shadow-xs px-4 py-2"
        >
          <Key className="h-4 w-4 mr-2" />
          Virtual Keys
        </TabsTrigger>
        <TabsTrigger
          value="services"
          className="rounded-lg text-xs font-semibold text-slate-600 data-active:bg-[#042B5F] data-active:text-white data-active:shadow-xs px-4 py-2"
        >
          <Server className="h-4 w-4 mr-2" />
          Dịch vụ liên kết
        </TabsTrigger>
        {isAdmin && (
          <TabsTrigger
            value="members"
            className="rounded-lg text-xs font-semibold text-slate-600 data-active:bg-[#042B5F] data-active:text-white data-active:shadow-xs px-4 py-2"
          >
            <Users className="h-4 w-4 mr-2" />
            Quản lý thành viên
          </TabsTrigger>
        )}
        <TabsTrigger
          value="settings"
          className="rounded-lg text-xs font-semibold text-slate-600 data-active:bg-[#042B5F] data-active:text-white data-active:shadow-xs px-4 py-2"
        >
          <Settings className="h-4 w-4 mr-2" />
          Cài đặt dự án
        </TabsTrigger>
      </TabsList>

      {/* Vault Tab (Phase 2) */}
      <TabsContent value="vault" className="space-y-4">
        <VaultView projectId={project.id} projectName={project.name} />
      </TabsContent>

      {/* Virtual Keys Tab (Phase 4 Zero-Trust Gatekeeper) */}
      <TabsContent value="keys" className="space-y-4">
        <VirtualKeysView projectId={project.id} />
      </TabsContent>

      {/* Allowed Services & Quotas Tab (Feature 012) */}
      <TabsContent value="services" className="space-y-4">
        <ProjectAllowedServicesView projectId={project.id} />
      </TabsContent>

      {/* Project Members Tab (Feature 019 - Admin only) */}
      {isAdmin && (
        <TabsContent value="members" className="space-y-4">
          <ProjectMembersView projectId={project.id} projectName={project.name} />
        </TabsContent>
      )}

      {/* Settings Tab */}
      <TabsContent value="settings" className="space-y-4">
        <Card className="min-h-[600px] border-slate-200 bg-white">
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
