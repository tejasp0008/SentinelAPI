"use client";

import { useEffect, useRef, useState } from "react";
import cytoscape from "cytoscape";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ApiEndpoint {
  id: string;
  endpoint: string;
  method: string;
  status: string;
  dynamic_risk_score: number;
}

// Define dependency relationships between API groups
const DEPENDENCY_MAP: Record<string, string[]> = {
  "/api/v2/auth/login": ["/api/v2/auth/refresh", "/api/v2/users/profile"],
  "/api/v2/auth/refresh": ["/api/v2/users/profile", "/api/v2/users/settings"],
  "/api/v2/users/profile": ["/api/v2/products/list"],
  "/api/v2/products/list": ["/api/v2/products/{id}", "/api/v2/payments/process"],
  "/api/v2/payments/process": ["/api/v2/notifications/send"],
  "/api/v2/files/upload": ["/api/v2/data/export"],
  "/api/v2/admin/users": ["/api/v2/config/update", "/api/v2/logs/download"],
  "/api/v2/webhooks/register": ["/api/v2/batch/process"],
  "/api/v1/legacy/users": ["/api/v1/legacy/orders", "/api/v1/legacy/reports"],
  "/api/v1/admin/config": ["/api/v1/internal/debug", "/api/v1/internal/metrics"],
  "/api/v1/legacy/search": ["/api/v1/legacy/export"],
};

function riskColor(score: number): string {
  if (score >= 80) return "#ef4444"; // red
  if (score >= 60) return "#f97316"; // orange
  if (score >= 40) return "#eab308"; // yellow
  return "#22c55e"; // green
}

function riskGlow(score: number): string {
  if (score >= 80) return "rgba(239,68,68,0.6)";
  if (score >= 60) return "rgba(249,115,22,0.4)";
  if (score >= 40) return "rgba(234,179,8,0.3)";
  return "rgba(34,197,94,0.2)";
}

export default function AttackGraph() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/apis`)
      .then((res) => res.json())
      .then((apis: ApiEndpoint[]) => {
        if (!containerRef.current) return;

        const nodes = apis.map((api) => ({
          data: {
            id: api.endpoint,
            label: api.endpoint.split("/").pop() || api.endpoint,
            riskScore: api.dynamic_risk_score,
            status: api.status,
            method: api.method,
            fullEndpoint: api.endpoint,
            color: riskColor(api.dynamic_risk_score),
            glow: riskGlow(api.dynamic_risk_score),
          },
        }));

        const edges: { data: { source: string; target: string } }[] = [];
        const nodeIds = new Set(apis.map((a) => a.endpoint));

        for (const [src, targets] of Object.entries(DEPENDENCY_MAP)) {
          if (!nodeIds.has(src)) continue;
          for (const target of targets) {
            if (nodeIds.has(target)) {
              edges.push({ data: { source: src, target } });
            }
          }
        }

        const cy = cytoscape({
          container: containerRef.current,
          elements: [...nodes, ...edges],
          style: [
            {
              selector: "node",
              style: {
                label: "data(label)",
                "background-color": "data(color)",
                "border-width": 2,
                "border-color": "data(color)",
                width: "mapData(riskScore, 0, 100, 30, 70)",
                height: "mapData(riskScore, 0, 100, 30, 70)",
                "font-size": "9px",
                color: "#e2e8f0",
                "text-valign": "bottom",
                "text-margin-y": 6,
                "text-outline-width": 1,
                "text-outline-color": "#0f172a",
                "shadow-blur": 15,
                "shadow-color": "data(glow)",
                "shadow-offset-x": 0,
                "shadow-offset-y": 0,
                "shadow-opacity": 0.8,
              } as any,
            },
            {
              selector: "edge",
              style: {
                width: 1.5,
                "line-color": "rgba(148,163,184,0.3)",
                "target-arrow-color": "rgba(148,163,184,0.5)",
                "target-arrow-shape": "triangle",
                "curve-style": "bezier",
                "arrow-scale": 0.8,
              },
            },
            {
              selector: "node:active",
              style: {
                "overlay-opacity": 0.2,
              },
            },
          ],
          layout: {
            name: "cose",
            animate: true,
            animationDuration: 1000,
            nodeRepulsion: () => 8000,
            idealEdgeLength: () => 120,
            gravity: 0.3,
            padding: 40,
          } as any,
          minZoom: 0.3,
          maxZoom: 3,
        });

        // Tooltip on tap
        cy.on("tap", "node", (evt) => {
          const node = evt.target;
          const d = node.data();
          alert(
            `Endpoint: ${d.fullEndpoint}\nMethod: ${d.method}\nStatus: ${d.status}\nRisk: ${d.riskScore}`
          );
        });

        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div className="rounded-2xl border border-white/10 bg-gray-900/80 backdrop-blur-xl overflow-hidden">
      <div className="p-5 border-b border-white/10 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="text-xl">🕸️</span> Attack Surface Graph
        </h2>
        <div className="flex gap-3 text-xs">
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-emerald-500 inline-block" />{" "}
            Low
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-amber-500 inline-block" />{" "}
            Medium
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-orange-500 inline-block" />{" "}
            High
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-red-500 inline-block" />{" "}
            Critical
          </span>
        </div>
      </div>
      <div className="relative" style={{ height: "450px" }}>
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900/50 z-10">
            <div className="flex flex-col items-center gap-3">
              <div className="w-10 h-10 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-sm text-gray-400">Loading graph...</p>
            </div>
          </div>
        )}
        <div ref={containerRef} className="w-full h-full" />
      </div>
    </div>
  );
}
