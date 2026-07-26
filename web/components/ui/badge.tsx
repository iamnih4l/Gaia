import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "border-transparent bg-cyan-500/15 text-cyan-400 border border-cyan-500/30",
        secondary: "border-transparent bg-slate-800 text-slate-300 border border-slate-700",
        destructive: "border-transparent bg-orange-500/15 text-orange-400 border border-orange-500/30 animate-pulse",
        success: "border-transparent bg-emerald-500/15 text-emerald-400 border border-emerald-500/30",
        warning: "border-transparent bg-amber-500/15 text-amber-400 border border-amber-500/30",
        purple: "border-transparent bg-purple-500/15 text-purple-400 border border-purple-500/30",
        outline: "text-slate-300 border border-white/20",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
