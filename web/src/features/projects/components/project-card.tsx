"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, Calendar, FolderKanban } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import type { Project } from "../types";

export interface ProjectCardProps {
  project: Project;
}

export function ProjectCard({ project }: ProjectCardProps) {
  const formattedDate = new Intl.DateTimeFormat("vi-VN", {
    dateStyle: "medium",
  }).format(new Date(project.created_at));

  return (
    <Link
      href={`/projects/${project.id}`}
      className="group block focus:outline-none focus-visible:ring-2 focus-visible:ring-[#042B5F] rounded-xl"
    >
      <Card className="h-full transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md hover:border-[#042B5F]/35 border-slate-200 bg-white flex flex-col justify-between">
        <div>
          <CardHeader className="space-y-2 pb-3">
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#EEF3FA] text-[#042B5F] transition-colors group-hover:bg-[#031F46] group-hover:text-white">
                  <FolderKanban className="h-4 w-4" />
                </div>
                <CardTitle className="text-base font-semibold text-slate-900 group-hover:text-[#042B5F] transition-colors">
                  {project.name}
                </CardTitle>
              </div>
            </div>
            <div className="flex items-center gap-1.5 pt-1">
              <Badge
                variant="secondary"
                className="font-mono text-[11px] bg-slate-100 text-slate-700 hover:bg-slate-200"
              >
                #{project.slug}
              </Badge>
            </div>
          </CardHeader>

          <CardContent className="pt-0 pb-4">
            <CardDescription className="text-xs text-slate-500 line-clamp-2 leading-relaxed">
              {project.description || "Chưa có mô tả cho dự án này."}
            </CardDescription>
          </CardContent>
        </div>

        <CardFooter className="flex items-center justify-between border-t border-slate-100 bg-slate-50/60 px-4 py-2.5 text-xs text-slate-500">
          <span className="flex items-center gap-1.5 text-[11px]">
            <Calendar className="h-3.5 w-3.5 text-slate-400" />
            {formattedDate}
          </span>
          <span className="flex items-center gap-1 font-medium text-[#042B5F] group-hover:translate-x-0.5 transition-transform text-xs">
            Workspace
            <ArrowRight className="h-3.5 w-3.5" />
          </span>
        </CardFooter>
      </Card>
    </Link>
  );
}
