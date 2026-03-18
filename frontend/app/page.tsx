"use client";

import { useState } from "react";
import SummaryCards from "./components/SummaryCards";
import ApiTable from "./components/ApiTable";
import AttackGraph from "./components/AttackGraph";

type TabId = "dashboard" | "inventory" | "attack-surface" | "ai-engine";

interface Tab {
  id: TabId;
  label: string;
  icon: string;
  description: string;
}

const TABS: Tab[] = [
  {
    id: "dashboard",
    label: "Dashboard",
    icon: "📊",
    description: "Overview & metrics",
  },
  {
    id: "inventory",
    label: "API Inventory",
    icon: "📡",
    description: "Discovered endpoints",
  },
  {
    id: "attack-surface",
    label: "Attack Surface",
    icon: "🕸️",
    description: "Dependency graph",
  },
  {
    id: "ai-engine",
    label: "AI Engine",
    icon: "🤖",
    description: "ML analysis status",
  },
];

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<TabId>("dashboard");

  return (
    <div className="min-h-screen flex flex-col">
      {/* ─── Top Navigation Bar ────────────────────────────────── */}
      <header className="sticky top-0 z-50 border-b border-white/10 bg-gray-950/80 backdrop-blur-xl">
        <div className="max-w-[1800px] mx-auto px-6 lg:px-10">
          {/* Brand + Status */}
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-lg shadow-lg shadow-cyan-500/20 shrink-0">
                🛡️
              </div>
              <div className="leading-tight">
                <h1 className="text-xl font-bold text-white tracking-tight">
                  Sentinel
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
                    API
                  </span>
                </h1>
                <p className="text-[11px] text-gray-500 -mt-0.5">
                  Zero-Trust Cybersecurity Platform
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
                </span>
                <span className="text-[11px] text-emerald-400 font-medium">
                  Operational
                </span>
              </div>
              <span className="text-[11px] text-gray-600 hidden sm:inline">
                AI: CNN + NLP + Isolation Forest
              </span>
            </div>
          </div>

          {/* Tab Navigation */}
          <nav className="flex gap-1 -mb-px">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`group relative flex items-center gap-2 px-5 py-3 text-sm font-medium transition-all duration-200 border-b-2 ${
                  activeTab === tab.id
                    ? "border-cyan-400 text-white"
                    : "border-transparent text-gray-500 hover:text-gray-300 hover:border-gray-700"
                }`}
              >
                <span className="text-base">{tab.icon}</span>
                <span className="hidden sm:inline">{tab.label}</span>
                {activeTab === tab.id && (
                  <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-8 h-0.5 bg-cyan-400 rounded-full blur-sm" />
                )}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* ─── Main Content ──────────────────────────────────────── */}
      <main className="flex-1 max-w-[1800px] w-full mx-auto px-6 lg:px-10 py-8">
        {/* Tab Header */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white tracking-tight">
            {TABS.find((t) => t.id === activeTab)?.label}
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            {TABS.find((t) => t.id === activeTab)?.description}
          </p>
        </div>

        {/* Tab Content */}
        <div className="animate-in fade-in duration-300">
          {activeTab === "dashboard" && <DashboardView />}
          {activeTab === "inventory" && <ApiTable />}
          {activeTab === "attack-surface" && <AttackGraph />}
          {activeTab === "ai-engine" && <AIEngineView />}
        </div>
      </main>

      {/* ─── Footer ────────────────────────────────────────────── */}
      <footer className="border-t border-white/5 py-6">
        <p className="text-center text-[11px] text-gray-600">
          SentinelAPI v1.0.0 — Phase 1 & 2 •{" "}
          <span className="text-gray-500">
            Blockchain & RL Pen-Testing coming in Phase 3
          </span>
        </p>
      </footer>
    </div>
  );
}

/* ─── Dashboard View (Summary Cards + Mini Table + Mini Graph) ─── */
function DashboardView() {
  return (
    <div className="space-y-8">
      <SummaryCards />

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        {/* Mini Attack Graph */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-300">
              Attack Surface Preview
            </h3>
            <span className="text-[11px] text-gray-600">
              Full view in Attack Surface tab
            </span>
          </div>
          <AttackGraph />
        </div>

        {/* Mini API Table */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-300">
              High-Risk Endpoints
            </h3>
            <span className="text-[11px] text-gray-600">
              Full inventory in API Inventory tab
            </span>
          </div>
          <ApiTable />
        </div>
      </div>
    </div>
  );
}

/* ─── AI Engine Status View ──────────────────────────────────── */
function AIEngineView() {
  const models = [
    {
      name: "CNN Anomaly Detector",
      tech: "PyTorch",
      status: "Active",
      icon: "🧠",
      description:
        "1D Convolutional Neural Network analyzing network traffic feature vectors for anomalous patterns. Processes 10-dimensional feature tensors for binary anomaly classification.",
      weight: "40%",
      color: "from-violet-500 to-purple-600",
    },
    {
      name: "NLP Payload Inspector",
      tech: "SpaCy + Regex",
      status: "Active",
      icon: "📝",
      description:
        "Inspects raw text payloads for SQL injection, XSS, command injection, and suspicious encoding patterns. Uses SpaCy for syntactic anomaly detection.",
      weight: "30%",
      color: "from-blue-500 to-indigo-600",
    },
    {
      name: "Isolation Forest Scorer",
      tech: "Scikit-learn",
      status: "Active",
      icon: "🌲",
      description:
        "Unsupervised anomaly detector fitted on synthetic baseline traffic. Scores behavioral anomalies based on payload size, request rate, and 8 other features.",
      weight: "30%",
      color: "from-emerald-500 to-teal-600",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Ensemble Overview */}
      <div className="rounded-2xl border border-white/10 bg-gray-900/80 backdrop-blur-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-2">
          AI Ensemble Pipeline
        </h3>
        <p className="text-sm text-gray-400 leading-relaxed mb-6">
          Incoming API telemetry is processed through three independent ML models.
          Their scores are combined using a weighted average to produce the final
          dynamic risk score. Endpoints exceeding the threshold (75) are
          automatically escalated.
        </p>

        <div className="flex items-center gap-3 flex-wrap">
          <span className="px-3 py-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-xs font-medium">
            Endpoint: POST /ai/analyze
          </span>
          <span className="px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-medium">
            Threshold: 75 / 100
          </span>
          <span className="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-medium">
            Auto-escalation: Enabled
          </span>
        </div>
      </div>

      {/* Model Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {models.map((model) => (
          <div
            key={model.name}
            className="rounded-2xl border border-white/10 bg-gray-900/80 backdrop-blur-xl overflow-hidden"
          >
            <div
              className={`h-1.5 bg-gradient-to-r ${model.color}`}
            />
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{model.icon}</span>
                  <div>
                    <h4 className="text-sm font-semibold text-white leading-tight">
                      {model.name}
                    </h4>
                    <p className="text-[11px] text-gray-500 mt-0.5">
                      {model.tech}
                    </p>
                  </div>
                </div>
                <span className="px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 text-[11px] font-medium">
                  {model.status}
                </span>
              </div>

              <p className="text-xs text-gray-400 leading-relaxed mb-4">
                {model.description}
              </p>

              <div className="flex items-center justify-between pt-4 border-t border-white/5">
                <span className="text-[11px] text-gray-500">
                  Ensemble Weight
                </span>
                <span className="text-sm font-bold text-white">
                  {model.weight}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Phase 3 Coming Soon */}
      <div className="rounded-2xl border border-dashed border-white/10 bg-gray-900/40 p-6">
        <div className="flex items-center gap-3 mb-3">
          <span className="text-2xl">🔮</span>
          <h3 className="text-sm font-semibold text-gray-400">
            Coming in Phase 3
          </h3>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="flex items-start gap-3 p-4 rounded-xl bg-white/[0.02]">
            <span className="text-lg mt-0.5">⛓</span>
            <div>
              <p className="text-sm font-medium text-gray-300">
                Blockchain Anchoring
              </p>
              <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                Ethereum smart contract for immutable alert audit trails via
                Web3.py integration.
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-4 rounded-xl bg-white/[0.02]">
            <span className="text-lg mt-0.5">🎯</span>
            <div>
              <p className="text-sm font-medium text-gray-300">
                RL Pen-Testing
              </p>
              <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                Reinforcement Learning agent for automated attack path discovery
                and vulnerability validation.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
