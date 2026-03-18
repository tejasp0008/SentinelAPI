"use client";

import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Props {
  endpointId: string;
  onComplete?: () => void;
}

type Phase = "idle" | "decommissioning" | "anchoring" | "scanning" | "done";

export default function DeactivateButton({ endpointId, onComplete }: Props) {
  const [phase, setPhase] = useState<Phase>("idle");
  const [result, setResult] = useState<string | null>(null);

  const handleClick = async () => {
    setPhase("decommissioning");

    try {
      // Step 1: Decommission
      await new Promise((r) => setTimeout(r, 600));
      setPhase("anchoring");

      // Step 2: Call backend
      const res = await fetch(`${API_URL}/decommission`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ endpoint_id: endpointId }),
      });

      if (!res.ok) throw new Error("Decommission failed");

      const data = await res.json();
      setPhase("scanning");

      // Step 3: Simulate RL scan delay
      await new Promise((r) => setTimeout(r, 1200));

      setPhase("done");
      setResult("Deactivated ✓");
      onComplete?.();
    } catch (err) {
      setPhase("idle");
      setResult("Error — retry");
    }
  };

  if (phase === "done") {
    return (
      <span className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-300 text-xs font-medium">
        ✅ {result}
      </span>
    );
  }

  if (phase !== "idle") {
    const labels: Record<Phase, { text: string; color: string }> = {
      decommissioning: {
        text: "Decommissioning...",
        color: "text-amber-300",
      },
      anchoring: {
        text: "⛓ Anchoring to Blockchain...",
        color: "text-cyan-300",
      },
      scanning: {
        text: "🎯 Initiating RL Scan...",
        color: "text-purple-300",
      },
      idle: { text: "", color: "" },
      done: { text: "", color: "" },
    };

    const { text, color } = labels[phase];

    return (
      <span
        className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 text-xs font-medium ${color}`}
      >
        <span className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin" />
        {text}
      </span>
    );
  }

  return (
    <button
      onClick={handleClick}
      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-500/20 text-red-300 border border-red-500/30 text-xs font-medium hover:bg-red-500/30 hover:text-red-200 transition-all duration-200 hover:shadow-lg hover:shadow-red-500/20 active:scale-95"
    >
      <span>⚡</span> Deactivate & Pen-Test
    </button>
  );
}
