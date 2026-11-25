/**
 * Utility for zero-persistence browser file downloads using native Blob and URL.createObjectURL.
 * Memory allocated for the download URL is immediately revoked after dispatch.
 */
export function downloadFile(
  filename: string,
  content: string,
  mimeType: string = "text/plain"
): void {
  if (typeof window === "undefined") return;

  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");

  anchor.href = url;
  anchor.download = filename;
  anchor.style.display = "none";
  document.body.appendChild(anchor);

  anchor.click();

  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}

/**
 * Generates deterministic, sanitized filenames for downloaded client mTLS certificates.
 */
export function getClientCertFilenames(deviceName: string): {
  crtFilename: string;
  keyFilename: string;
} {
  const slug = deviceName.toLowerCase().replace(/[^a-z0-9]/g, "-") || "device";
  return {
    crtFilename: `${slug}-client.crt`,
    keyFilename: `${slug}-client.key`,
  };
}
