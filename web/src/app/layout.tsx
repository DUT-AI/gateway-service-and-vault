import type { Metadata } from "next";
import NextTopLoader from "nextjs-toploader";
import { JetBrains_Mono, Plus_Jakarta_Sans } from "next/font/google";
import Providers from "./providers";
import { cn } from "@/lib/utils";
import "./globals.css";

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ["latin", "vietnamese"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-sans",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin", "vietnamese"],
  weight: ["400", "500", "600"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "DUT-AI Gateway & Vault",
  description: "Zero-Trust API Gateway & Dynamic Secret Vault Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="vi"
      className={cn(
        "h-full antialiased",
        "font-sans",
        plusJakarta.variable,
        jetbrainsMono.variable
      )}
      suppressHydrationWarning
    >
      <body className="min-h-full" suppressHydrationWarning>
        <NextTopLoader color="#042B5F" height={3} showSpinner={false} />
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
