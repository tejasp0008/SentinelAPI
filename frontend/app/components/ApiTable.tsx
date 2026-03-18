"use client";

import { useEffect, useState, useCallback } from "react";
import DeactivateButton from "./DeactivateButton";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ApiEndpoint {
  id: string;
  endpoint: string;
  method: string;
  status: string;
  auth_type: string | null;
  encryption: string | null;
  dynamic_risk_score: number;
  last_used: string | null;
  traffic_count: number;
  days_since_last_used: number;
  vulnerabilities: string | null;
}

const METHOD_COLORS: Record<string, string> = {
  GET: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
  POST: "bg-blue-500/20 text-blue-300 border-blue-500/30",
  PUT: "bg-amber-500/20 text-amber-300 border-amber-500/30",
  DELETE: "bg-red-500/20 text-red-300 border-red-500/30",
  PATCH: "bg-purple-500/20 text-purple-300 border-purple-500/30",
};

const STATUS_COLORS: Record<string, string> = {
  active: "bg-emerald-500/20 text-emerald-300",
  deprecated: "bg-amber-500/20 text-amber-300",
  zombie: "bg-red-500/20 text-red-300",
  shadow: "bg-purple-500/20 text-purple-300",
  inactive: "bg-gray-500/20 text-gray-400",
  vulnerable: "bg-orange-500/20 text-orange-300",
};

function riskBadge(score: number) {
  if (score >= 80)
    return "bg-red-500/30 text-red-300 border border-red-500/50 animate-pulse";
  if (score >= 60)
    return "bg-orange-500/20 text-orange-300 border border-orange-500/40";
  if (score >= 40)
    return "bg-amber-500/20 text-amber-300 border border-amber-500/40";
  return "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40";
}

export default function ApiTable() {
  const [apis, setApis] = useState<ApiEndpoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("all");

  const fetchApis = useCallback(() => {
    setLoading(true);
    const url =
      filter === "all"
        ? `${API_URL}/apis`
        : `${API_URL}/apis?status_filter=${filter}`;
    fetch(url)
      .then((res) => res.json())
      .then((data) => {
        setApis(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [filter]);

  useEffect(() => {
    fetchApis();
  }, [fetchApis]);

  const filters = [
    "all",
    "active",
    "zombie",
    "deprecated",
    "shadow",
    "inactive",
  ];

  return (
    <div className="rounded-2xl border border-white/10 bg-gray-900/80 backdrop-blur-xl overflow-hidden">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-5 border-b border-white/10">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="text-xl">📡</span> API Inventory
        </h2>
        <div className="flex gap-2 mt-3 sm:mt-0 flex-wrap">
          {filters.map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-all duration-200 capitalize ${
                filter === f
                  ? "bg-blue-500 text-white shadow-lg shadow-blue-500/30"
                  : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-white/5">
              <th className="text-left p-4 text-gray-400 font-medium whitespace-nowrap">
                Endpoint
              </th>
              <th className="text-left p-4 text-gray-400 font-medium whitespace-nowrap">
                Method
              </th>
              <th className="text-left p-4 text-gray-400 font-medium whitespace-nowrap">
                Status
              </th>
              <th className="text-left p-4 text-gray-400 font-medium whitespace-nowrap">
                Auth
              </th>
              <th className="text-left p-4 text-gray-400 font-medium whitespace-nowrap">
                Encryption
              </th>
              <th className="text-left p-4 text-gray-400 font-medium whitespace-nowrap">
                Risk
              </th>
              <th className="text-left p-4 text-gray-400 font-medium whitespace-nowrap">
                Traffic
              </th>
              <th className="text-left p-4 text-gray-400 font-medium whitespace-nowrap">
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="border-b border-white/5">
                  {Array.from({ length: 8 }).map((_, j) => (
                    <td key={j} className="p-4">
                      <div className="h-4 bg-white/5 rounded animate-pulse w-24" />
                    </td>
                  ))}
                </tr>
              ))
            ) : apis.length === 0 ? (
              <tr>
                <td colSpan={8} className="p-8 text-center text-gray-500">
                  No APIs found. Start the backend and seed the database.
                </td>
              </tr>
            ) : (
              apis.map((api) => (
                <tr
                  key={api.id}
                  className="border-b border-white/5 hover:bg-white/5 transition-colors duration-150"
                >
                  <td className="p-4">
                    <code className="text-cyan-300 text-xs bg-cyan-500/10 px-2 py-1 rounded whitespace-nowrap">
                      {api.endpoint}
                    </code>
                  </td>
                  <td className="p-4">
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-bold border ${
                        METHOD_COLORS[api.method] ||
                        "bg-gray-500/20 text-gray-300"
                      }`}
                    >
                      {api.method}
                    </span>
                  </td>
                  <td className="p-4">
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium capitalize whitespace-nowrap ${
                        STATUS_COLORS[api.status] ||
                        "bg-gray-500/20 text-gray-300"
                      }`}
                    >
                      {api.status}
                    </span>
                  </td>
                  <td className="p-4 text-gray-300 text-xs whitespace-nowrap">
                    {api.auth_type || (
                      <span className="text-red-400 font-medium">⚠ None</span>
                    )}
                  </td>
                  <td className="p-4 text-gray-300 text-xs whitespace-nowrap">
                    {api.encryption || (
                      <span className="text-red-400 font-medium">⚠ None</span>
                    )}
                  </td>
                  <td className="p-4">
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-bold whitespace-nowrap ${riskBadge(
                        api.dynamic_risk_score
                      )}`}
                    >
                      {api.dynamic_risk_score}
                    </span>
                  </td>
                  <td className="p-4 text-gray-300 text-xs tabular-nums whitespace-nowrap">
                    {api.traffic_count.toLocaleString()}
                  </td>
                  <td className="p-4">
                    {api.dynamic_risk_score >= 50 &&
                    api.status !== "inactive" ? (
                      <DeactivateButton
                        endpointId={api.id}
                        onComplete={fetchApis}
                      />
                    ) : null}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
