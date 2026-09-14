import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "border-line bg-surface-subtle text-ink-secondary",
        positive: "border-transparent bg-edge-positive-soft text-edge-positive",
        negative: "border-transparent bg-edge-negative-soft text-edge-negative",
        warning: "border-transparent bg-edge-warning-soft text-edge-warning",
        info: "border-transparent bg-edge-info-soft text-edge-info",
        outline: "border-line text-ink bg-transparent",
        solid: "border-transparent bg-primary text-primary-foreground",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
