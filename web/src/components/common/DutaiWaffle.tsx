"use client";

import React from "react";
import Script from "next/script";

export interface DutaiWaffleProps {
  current?: "manage" | "lms" | "meetly" | "data" | string;
  className?: string;
}

export function DutaiWaffle({ current = "data", className }: DutaiWaffleProps) {
  return (
    <div className={`inline-flex items-center ${className ?? ""}`}>
      <Script
        src="https://workspace.dutai.io.vn/waffle.js"
        strategy="lazyOnload"
      />
      <dutai-waffle current={current} suppressHydrationWarning />
    </div>
  );
}

export default DutaiWaffle;
