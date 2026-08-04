"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { bookingsByType } from "@/data/analytics";

const colors: Record<string, string> = {
  "Hotel Rooms": "#0e2f73",
  Villas: "#d80b0b",
  Houses: "#8da8e1",
};

export function BookingsByTypeChart() {
  const total = bookingsByType.reduce((sum, d) => sum + d.value, 0);

  return (
    <div className="flex items-center gap-4">
      <div className="relative h-44 w-44 shrink-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={bookingsByType}
              dataKey="value"
              nameKey="type"
              innerRadius={52}
              outerRadius={72}
              paddingAngle={3}
              animationDuration={900}
              stroke="none"
            >
              {bookingsByType.map((entry) => (
                <Cell key={entry.type} fill={colors[entry.type]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-heading text-xl font-extrabold text-primary-900">{total}</span>
          <span className="text-[11px] text-slate-400">Bookings</span>
        </div>
      </div>

      <div className="space-y-2.5">
        {bookingsByType.map((d) => (
          <div key={d.type} className="flex items-center gap-2 text-sm">
            <span
              className="h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: colors[d.type] }}
            />
            <span className="text-slate-600">{d.type}</span>
            <span className="font-semibold text-primary-900">{d.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
