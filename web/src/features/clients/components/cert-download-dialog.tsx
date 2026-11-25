"use client";

import React, { useState } from "react";
import {
  AlertTriangle,
  Check,
  CheckCircle2,
  Copy,
  Download,
  FileText,
  KeyRound,
  ShieldCheck,
} from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useAuth } from "@/contexts/auth-context";
import { downloadFile, getClientCertFilenames } from "../utils/download-file";
import { CertInstallInstructions } from "./cert-install-instructions";
import { CertNextStepsCard } from "./cert-next-steps-card";
import type { RegisterClientResult } from "../types";

export interface CertDownloadDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  bundle: RegisterClientResult | null;
  onOpenDockerGuide?: () => void;
}

export function CertDownloadDialog({
  open,
  onOpenChange,
  bundle,
  onOpenDockerGuide,
}: CertDownloadDialogProps) {
  const { isOtherRole } = useAuth();
  const [copiedFingerprint, setCopiedFingerprint] = useState(false);
  const [downloadedCrt, setDownloadedCrt] = useState(false);
  const [downloadedKey, setDownloadedKey] = useState(false);

  if (!bundle) return null;

  const { crtFilename, keyFilename } = getClientCertFilenames(bundle.name);
  const step1Done = downloadedCrt && downloadedKey;

  const handleCopyFingerprint = async () => {
    try {
      await navigator.clipboard.writeText(bundle.cert_fingerprint);
      setCopiedFingerprint(true);
      toast.success("Đã sao chép SHA-256 Fingerprint vào bộ nhớ tạm");
      setTimeout(() => setCopiedFingerprint(false), 2000);
    } catch {
      toast.error("Không thể sao chép fingerprint");
    }
  };

  const handleDownloadCrt = () => {
    downloadFile(crtFilename, bundle.cert_pem, "application/x-x509-ca-cert");
    setDownloadedCrt(true);
    toast.success("Đã tải chứng chỉ X.509 (client.crt)");
  };

  const handleDownloadKey = () => {
    downloadFile(keyFilename, bundle.key_pem, "application/pkcs8");
    setDownloadedKey(true);
    toast.success("Đã tải khóa riêng mTLS (client.key)");
  };

  const handleDownloadBoth = () => {
    handleDownloadCrt();
    setTimeout(() => {
      handleDownloadKey();
    }, 300);
    toast.success("Đang tải cả hai tệp chứng chỉ & khóa riêng...");
  };

  const confirmCloseIfKeyMissing = () => {
    if (!downloadedKey) {
      return window.confirm(
        "Bạn chưa tải khóa riêng (client.key). Nếu đóng cửa sổ này, bạn sẽ không thể lấy lại khóa này nữa. Bạn có chắc chắn muốn đóng?"
      );
    }
    return true;
  };

  const handleDialogOpenChange = (nextOpen: boolean) => {
    if (!nextOpen && !confirmCloseIfKeyMissing()) {
      return;
    }
    onOpenChange(nextOpen);
  };

  const handleFinish = () => {
    handleDialogOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleDialogOpenChange}>
      <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-2.5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <DialogTitle className="text-base font-semibold text-slate-900">
                Chứng chỉ mTLS đã được cấp phát
              </DialogTitle>
              <DialogDescription className="text-xs text-slate-500">
                Thiết bị <strong className="text-slate-800">{bundle.name}</strong>{" "}
                đã được đăng ký thành công vào hệ thống Zero-Trust Gateway.
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        {/* One-time Private Key Security Alert */}
        <div className="rounded-xl border border-amber-200 bg-amber-50/80 p-3.5 space-y-1.5 text-xs text-amber-900">
          <div className="flex items-center gap-2 font-semibold text-amber-950">
            <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0" />
            <span>Lưu ý bảo mật quan trọng (Chỉ hiển thị 1 lần)</span>
          </div>
          <p className="leading-relaxed text-amber-800 text-[11px]">
            Khóa riêng tư (Private Key) được tạo lập trực tiếp và{" "}
            <strong>tuyệt đối không được lưu trữ</strong> trên máy chủ trung tâm.
            Hãy hoàn thành 3 bước bên dưới trước khi đóng cửa sổ này.
          </p>
        </div>

        {/* Certificate Metadata Summary */}
        <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-3.5 space-y-2.5 text-xs">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div>
              <span className="text-slate-500 font-medium">Tên thiết bị:</span>
              <p className="font-semibold text-slate-800 mt-0.5 truncate">
                {bundle.name}
              </p>
            </div>
            <div>
              <span className="text-slate-500 font-medium">Loại Client:</span>
              <div className="mt-0.5">
                <Badge variant="outline" className="text-[11px] font-semibold bg-white">
                  {bundle.client_type === "USER_DEVICE"
                    ? "Developer PC"
                    : "Workload Server"}
                </Badge>
              </div>
            </div>
            <div className="col-span-2 sm:col-span-1">
              <span className="text-slate-500 font-medium">Hạn hiệu lực:</span>
              <p className="text-slate-700 mt-0.5">
                {new Date(bundle.expires_at).toLocaleDateString("vi-VN")}
              </p>
            </div>
          </div>

          <div className="border-t border-slate-200/80 pt-2.5">
            <div className="flex items-center justify-between">
              <span className="text-slate-500 font-medium">
                Fingerprint SHA-256:
              </span>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={handleCopyFingerprint}
                className="h-6 px-2 text-xs text-slate-600 hover:text-slate-900"
              >
                {copiedFingerprint ? (
                  <>
                    <Check className="h-3 w-3 mr-1 text-emerald-600" />
                    Đã chép
                  </>
                ) : (
                  <>
                    <Copy className="h-3 w-3 mr-1 text-slate-500" />
                    Sao chép
                  </>
                )}
              </Button>
            </div>
            <p className="font-mono text-[11px] text-slate-700 bg-white border border-slate-200 px-2.5 py-1.5 rounded-lg mt-1 break-all select-all">
              {bundle.cert_fingerprint}
            </p>
          </div>
        </div>

        {/* Step 1: Download Certificates */}
        <div
          className={`rounded-xl border p-3.5 space-y-2.5 ${
            step1Done
              ? "border-emerald-200 bg-emerald-50/40"
              : "border-slate-200 bg-white"
          }`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {step1Done ? (
                <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
              ) : (
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-blue-100 text-[11px] font-bold text-blue-700">
                  1
                </span>
              )}
              <span className="text-xs font-semibold text-slate-800">
                Tải tệp chứng chỉ & khóa riêng về máy
              </span>
            </div>
            {step1Done && (
              <Badge
                variant="outline"
                className="text-[10px] bg-emerald-50 text-emerald-700 border-emerald-200"
              >
                Đã tải đủ 2 tệp
              </Badge>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={handleDownloadCrt}
              className={`h-11 justify-start border-slate-200 text-xs font-medium ${
                downloadedCrt ? "border-emerald-300 bg-emerald-50/60" : "bg-white"
              }`}
            >
              <FileText className="h-4 w-4 mr-2 text-blue-600" />
              <div className="text-left flex-1">
                <div>Tải client.crt</div>
                <div className="text-[10px] text-slate-500">
                  Public X.509 Certificate
                </div>
              </div>
              {downloadedCrt && <Check className="h-4 w-4 text-emerald-600" />}
            </Button>

            <Button
              type="button"
              variant="outline"
              onClick={handleDownloadKey}
              className={`h-11 justify-start border-slate-200 text-xs font-medium ${
                downloadedKey ? "border-emerald-300 bg-emerald-50/60" : "bg-white"
              }`}
            >
              <KeyRound className="h-4 w-4 mr-2 text-amber-600" />
              <div className="text-left flex-1">
                <div>Tải client.key</div>
                <div className="text-[10px] text-slate-500">
                  Private Key (PKCS#8)
                </div>
              </div>
              {downloadedKey && <Check className="h-4 w-4 text-emerald-600" />}
            </Button>
          </div>

          <Button
            type="button"
            variant="default"
            onClick={handleDownloadBoth}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs h-9"
          >
            <Download className="h-4 w-4 mr-2" />
            Tải cả hai tệp (client.crt & client.key)
          </Button>
        </div>

        {/* Step 2: Install & Secure Files */}
        <CertInstallInstructions
          key={bundle.id}
          crtFilename={crtFilename}
          keyFilename={keyFilename}
          clientType={bundle.client_type}
        />

        {/* Step 3: Role-Aware Next Steps & Verification */}
        <CertNextStepsCard
          bundle={bundle}
          isOtherRole={isOtherRole}
          onNavigateToProjects={() => onOpenChange(false)}
          onOpenDockerGuide={
            onOpenDockerGuide
              ? () => {
                  if (confirmCloseIfKeyMissing()) {
                    onOpenChange(false);
                    onOpenDockerGuide();
                  }
                }
              : undefined
          }
        />

        <DialogFooter className="pt-2 border-t border-slate-100">
          <Button
            type="button"
            variant={step1Done ? "default" : "outline"}
            onClick={handleFinish}
            className={`w-full sm:w-auto text-xs ${
              step1Done
                ? "bg-emerald-600 hover:bg-emerald-700 text-white"
                : ""
            }`}
          >
            {step1Done ? "Hoàn tất" : "Đã lưu an toàn & Hoàn tất"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
