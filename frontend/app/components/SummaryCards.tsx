"use client";

import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface SummaryData {
  totalApis: number;
  zombiesDetected: number;
  avgRisk: number;
  criticalCount: number;
  activeCount: number;
}

export default function SummaryCards() {
  const [data, setData] = useState<SummaryData>({
    totalApis: 0,
    zombiesDetected: 0,
    avgRisk: 0,
    criticalCount: 0,
    activeCount: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/apis`)
      .then((res) => res.json())
      .then((apis: any[]) => {
        const total = apis.length;
        const zombies = apis.filter(
          (a) => a.status === "zombie" || a.status === "deprecated"
        ).length;
        const avg =
          total > 0
            ? apis.reduce((sum, a) => sum + a.dynamic_risk_score, 0) / total
            : 0;
        const critical = apis.filter(
          (a) => a.dynamic_risk_score >= 80
        ).length;
        const active = apis.filter((a) => a.status === "active").length;

        setData({
          totalApis: total,
          zombiesDetected: zombies,
          avgRisk: Math.round(avg * 10) / 10,
          criticalCount: critical,
          activeCount: active,
        });
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const cards = [
    {
      label: "Total APIs",
      value: data.totalApis,
      icon: "🌐",
      gradient: "from-blue-500 to-cyan-400",
      shadow: "shadow-blue-500/25",
    },
    {
      label: "Zombies Detected",
      value: data.zombiesDetected,
      icon: "💀",
      gradient: "from-red-500 to-orange-400",
      shadow: "shadow-red-500/25",
    },
    {
      label: "Avg Risk Score",
      value: data.avgRisk,
      icon: "⚡",
      gradient: "from-amber-500 to-yellow-400",
      shadow: "shadow-amber-500/25",
    },
    {
      label: "Critical Alerts",
      value: data.criticalCount,
      icon: "🚨",
      gradient: "from-rose-500 to-pink-400",
      shadow: "shadow-rose-500/25",
    },
    {
      label: "Active APIs",
      value: data.activeCount,
      icon: "✅",
      gradient: "from-emerald-500 to-green-400",
      shadow: "shadow-emerald-500/25",
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-5 items-stretch">
      {cards.map((card) => (
        <div
          key={card.label}
          className={`relative overflow-hidden rounded-2xl bg-gradient-to-br ${card.gradient} p-5 text-white shadow-lg ${card.shadow} transition-all duration-300 hover:scale-[1.03] hover:shadow-xl flex flex-col justify-between min-h-[110px]`}
        >
          <div className="absolute -top-3 -right-3 text-5xl opacity-15 select-none pointer-events-none">
            {card.icon}
          </div>
          <p className="text-sm font-medium opacity-90 leading-tight">
            {card.label}
          </p>
          <p className="mt-3 text-3xl font-bold tracking-tight">
            {loading ? (
              <span className="inline-block w-14 h-8 bg-white/20 rounded animate-pulse" />
            ) : (
              card.value
            )}
          </p>
        </div>
      ))}
    </div>
  );
}
