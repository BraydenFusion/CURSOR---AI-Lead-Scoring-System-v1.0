import { HTMLAttributes } from "react";
import { clsx } from "clsx";

interface BadgeProps extends HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "destructive" | "outline";
}

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <div
      className={clsx(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors",
        {
          "bg-blue-600 text-white": variant === "default",
          "bg-gray-100 text-gray-800": variant === "secondary",
          "bg-red-500 text-white": variant === "destructive",
          "border border-gray-300 bg-transparent": variant === "outline",
        },
        className
      )}
      {...props}
    />
  );
}

