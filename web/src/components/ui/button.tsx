import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex shrink-0 items-center justify-center rounded-lg border border-transparent bg-clip-padding text-sm font-medium whitespace-nowrap transition-all outline-none select-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
  {
    variants: {
      variant: {
        default: "bg-[#042B5F] text-white hover:bg-[#031F46] shadow-2xs",
        primary: "bg-[#042B5F] text-white hover:bg-[#031F46] shadow-2xs",
        outline:
          "border border-slate-200 bg-white hover:bg-[#EEF3FA] hover:border-[#042B5F]/25 hover:text-[#042B5F] text-slate-800",
        secondary: "bg-[#EEF3FA] text-[#042B5F] hover:bg-[#E1EAF6]",
        ghost: "hover:bg-slate-100 text-slate-700 hover:text-slate-950",
        destructive: "bg-rose-600 text-white hover:bg-rose-700 shadow-2xs",
        link: "text-[#042B5F] underline-offset-4 hover:underline",
      },
      size: {
        default: "h-9 px-4 py-2",
        xs: "h-6 px-2 text-xs",
        sm: "h-8 px-3 text-xs",
        lg: "h-10 px-5 text-base",
        icon: "h-9 w-9",
        "icon-sm": "h-7 w-7",
        "icon-lg": "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
