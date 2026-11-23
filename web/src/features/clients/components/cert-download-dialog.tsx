"use client";

import React, { useState } from "react";
import {
  AlertTriangle,
  Check,
  Copy,
  Download,
  FileKey2,
  FileText,
  KeyRound,
  ShieldCheck,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { downloadFile } from "../utils/download-file";
import type { RegisterClientResult } from "../types";

export interface CertDownloadDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  bundle: RegisterClientResult | null;
}

export function CertDownloadDialog({
  open,
  onOpenChange,
  bundle,
}: CertDownloadDialogProps) {
  const [copiedFingerprint, setCopiedFingerprint] = useState(false);
  const [downloadedCrt, setDownloadedCrt] = useState(false);
  const [downloadedKey, setDownloadedKey] = useState(false);

  if (!bundle) return null;

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
    downloadFile(
      `${bundle.name.toLowerCase().replace(/[^a-z0-9]/g, "-")}-client.crt`,
      bundle.cert_pem,
      "application/x-x509-ca-cert"
    );
    setDownloadedCrt(true);
    toast.success("Đã tải chứng chỉ X.509 (client.crt)");
  };

  const handleDownloadKey = () => {
    downloadFile(
      `${bundle.name.toLowerCase().replace(/[^a-z0-9]/g, "-")}-client.key`,
      bundle.key_pem,
      "application/pkcs8"
    );
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

  const handleFinish = () => {
    if (!downloadedKey) {
      const confirmDismiss = window.confirm(
        "Bạn chưa tải khóa riêng (client.key). Nếu đóng cửa sổ này, bạn sẽ không thể lấy lại khóa này nữa. Bạn có chắc chắn muốn đóng?"
      );
      if (!confirmDismiss) return;
    }
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-xl max-h-[90vh] overflow-y-auto">
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

        {/* Security Alert */}
        <div className="rounded-xl border border-amber-200 bg-amber-50/80 p-4 space-y-2 text-xs text-amber-900">
          <div className="flex items-center gap-2 font-semibold text-amber-950">
            <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0" />
            <span>Lưu ý bảo mật quan trọng (Chỉ hiển thị 1 lần)</span>
          </div>
          <p className="leading-relaxed text-amber-800">
            Khóa riêng tư (Private Key) được tạo lập trực tiếp và{" "}
            <strong>tuyệt đối không được lưu trữ</strong> trên máy chủ trung tâm.
            Hãy tải ngay cả hai tệp về máy và chuyển vào thư mục cấu hình an toàn
            (ví dụ: <code className="font-mono bg-amber-100 px-1 py-0.5 rounded">~/.dut-vault/</code>).
          </p>
        </div>

        {/* Certificate Metadata */}
        <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4 space-y-3 text-xs">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <span className="text-slate-500 font-medium">Tên thiết bị:</span>
              <p className="font-semibold text-slate-800 mt-0.5">{bundle.name}</p>
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
          </div>

          <div className="border-t border-slate-200/80 pt-3">
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
            <p className="font-mono text-[11px] text-slate-700 bg-white border border-slate-200 p-2 rounded-lg mt-1 break-all select-all">
              {bundle.cert_fingerprint}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 border-t border-slate-200/80 pt-3">
            <div>
              <span className="text-slate-500 font-medium">Serial Number:</span>
              <p className="font-mono text-[11px] text-slate-700 truncate mt-0.5">
                {bundle.cert_serial}
              </p>
            </div>
            <div>
              <span className="text-slate-500 font-medium">Hạn hiệu lực:</span>
              <p className="text-slate-700 mt-0.5">
                {new Date(bundle.expires_at).toLocaleString("vi-VN")}
              </p>
            </div>
          </div>
        </div>

        {/* Download Buttons Section */}
        <div className="space-y-2 pt-1">
          <p className="text-xs font-semibold text-slate-700">
            Tải tệp chứng chỉ & khóa riêng:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={handleDownloadCrt}
              className={`h-11 justify-start border-slate-200 text-xs font-medium ${
                downloadedCrt ? "border-emerald-300 bg-emerald-50/50" : ""
              }`}
            >
              <FileText className="h-4 w-4 mr-2 text-blue-600" />
              <div className="text-left flex-1">
                <div>Tải client.crt</div>
                <div className="text-[10px] text-slate-500">Public X.509 Certificate</div>
              </div>
              {downloadedCrt && <Check className="h-4 w-4 text-emerald-600" />}
            </Button>

            <Button
              type="button"
              variant="outline"
              onClick={handleDownloadKey}
              className={`h-11 justify-start border-slate-200 text-xs font-medium ${
                downloadedKey ? "border-emerald-300 bg-emerald-50/50" : ""
              }`}
            >
              <KeyRound className="h-4 w-4 mr-2 text-amber-600" />
              <div className="text-left flex-1">
                <div>Tải client.key</div>
                <div className="text-[10px] text-slate-500">Private Key (PKCS#8)</div>
              </div>
              {downloadedKey && <Check className="h-4 w-4 text-emerald-600" />}
            </Button>
          </div>

          <Button
            type="button"
            variant="default"
            onClick={handleDownloadBoth}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs h-10 mt-2"
          >
            <Download className="h-4 w-4 mr-2" />
            Tải cả hai tệp (client.crt & client.key)
          </Button>
        </div>

        <DialogFooter className="pt-2 border-t border-slate-100">
          <Button
            type="button"
            variant="outline"
            onClick={handleFinish}
            className="w-full sm:w-auto text-xs"
          >
            Đã lưu an toàn & Hoàn tất
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
