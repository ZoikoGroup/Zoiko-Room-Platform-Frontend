"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { occupancyByCity } from "@/data/analytics";

export function OccupancyChart() {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={occupancyByCity} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke="#eef2fa" />
          <XAxis dataKey="city" axisLine={false} tickLine={false} tick={{ fill: "#64748b", fontSize: 12 }} />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fill: "#64748b", fontSize: 12 }}
            tickFormatter={(v) => `${v}%`}
            width={40}
          />
          <Tooltip
            formatter={(value) => `${value}% occupancy`}
            contentStyle={{
              borderRadius: 12,
              border: "1px solid #fdecec",
              boxShadow: "0 8px 24px rgba(216,11,11,0.1)",
            }}
          />
          <Bar dataKey="occupancy" fill="#d80b0b" radius={[8, 8, 0, 0]} animationDuration={900} maxBarSize={36} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
