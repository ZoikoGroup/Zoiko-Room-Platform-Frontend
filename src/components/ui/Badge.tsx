import { cn } from "@/lib/utils";

type Tone = "primary" | "accent" | "success" | "warning" | "neutral" | "danger";

const toneClasses: Record<Tone, string> = {
  primary: "bg-primary-50 text-primary-700 ring-1 ring-primary-200",
  accent: "bg-accent-50 text-accent-700 ring-1 ring-accent-200",
  success: "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200",
  warning: "bg-amber-50 text-amber-700 ring-1 ring-amber-200",
  danger: "bg-rose-50 text-rose-700 ring-1 ring-rose-200",
  neutral: "bg-slate-100 text-slate-600 ring-1 ring-slate-200",
};

export function Badge({
  children,
  tone = "neutral",
  className,
  dot,
}: {
  children: React.ReactNode;
  tone?: Tone;
  className?: string;
  dot?: boolean;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold whitespace-nowrap",
        toneClasses[tone],
        className
      )}
    >
      {dot && <span className="h-1.5 w-1.5 rounded-full bg-current" />}
      {children}
    </span>
  );
}
