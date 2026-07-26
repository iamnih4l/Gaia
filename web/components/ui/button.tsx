import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-lg font-mono text-xs font-semibold tracking-wider uppercase transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500 disabled:pointer-events-none disabled:opacity-40 cursor-pointer select-none active:scale-[0.98]",
  {
    variants: {
      variant: {
        default:
          "bg-white/[0.06] text-white hover:bg-cyan-500/15 hover:text-cyan-300 border border-white/15 hover:border-cyan-400/70 shadow-[0_0_15px_rgba(0,242,254,0.1)] hover:shadow-[0_0_25px_rgba(0,242,254,0.35)] backdrop-blur-xl",
        destructive:
          "bg-orange-500/15 text-orange-400 hover:bg-orange-500/25 border border-orange-500/40 hover:border-orange-400 shadow-[0_0_15px_rgba(249,115,22,0.15)] hover:shadow-[0_0_25px_rgba(249,115,22,0.35)] backdrop-blur-xl",
        outline:
          "border border-white/12 bg-black/60 hover:bg-cyan-500/10 hover:border-cyan-400/50 hover:text-cyan-300 text-slate-300 backdrop-blur-xl shadow-sm hover:shadow-[0_0_20px_rgba(0,242,254,0.2)]",
        secondary:
          "bg-slate-900/80 text-slate-200 hover:bg-cyan-500/10 hover:text-cyan-300 hover:border-cyan-500/40 border border-white/10 backdrop-blur-xl hover:shadow-[0_0_15px_rgba(0,242,254,0.15)]",
        ghost:
          "hover:bg-cyan-500/15 hover:text-cyan-300 text-slate-400 border border-transparent hover:border-cyan-500/30",
        link:
          "text-cyan-400 underline-offset-4 hover:underline hover:text-cyan-300 hover:drop-shadow-[0_0_8px_rgba(0,242,254,0.6)]",
        gradient:
          "bg-gradient-to-r from-cyan-500 via-teal-400 to-emerald-400 text-slate-950 hover:opacity-95 font-bold shadow-[0_0_25px_rgba(0,242,254,0.35)] hover:shadow-[0_0_35px_rgba(0,242,254,0.6)] border border-cyan-300/60",
        purple:
          "bg-purple-500/15 text-purple-300 hover:bg-purple-500/25 border border-purple-500/40 hover:border-purple-400 shadow-[0_0_15px_rgba(168,85,247,0.2)] hover:shadow-[0_0_25px_rgba(168,85,247,0.4)] backdrop-blur-xl",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-7 rounded-md px-3 text-[11px]",
        lg: "h-11 rounded-xl px-6 text-sm",
        icon: "h-9 w-9",
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
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
