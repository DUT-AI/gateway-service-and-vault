import * as React from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

export interface NativeSelectProps
  extends React.SelectHTMLAttributes<HTMLSelectElement> {
  wrapperClassName?: string;
}

export const NativeSelect = React.forwardRef<
  HTMLSelectElement,
  NativeSelectProps
>(({ className, wrapperClassName, children, ...props }, ref) => {
  return (
    <div className={cn("relative w-full", wrapperClassName)}>
      <select
        ref={ref}
        className={cn(
          "w-full h-9 appearance-none rounded-lg border border-slate-200 bg-white pl-3 pr-9 text-xs text-slate-800 outline-none transition-colors focus:border-[#042B5F] focus:ring-1 focus:ring-[#042B5F] disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        {...props}
      >
        {children}
      </select>
      <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
    </div>
  );
});

NativeSelect.displayName = "NativeSelect";
