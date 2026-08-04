import { Star } from "lucide-react";

export function StarRating({ rating, size = 14 }: { rating: number; size?: number }) {
  return (
    <div className="inline-flex items-center gap-0.5">
      {Array.from({ length: 5 }).map((_, i) => {
        const filled = i + 1 <= Math.round(rating);
        return (
          <Star
            key={i}
            size={size}
            className={
              filled
                ? "fill-accent-500 text-accent-500"
                : "fill-slate-200 text-slate-200 dark:fill-slate-700 dark:text-slate-700"
            }
          />
        );
      })}
    </div>
  );
}
