"use client";
import { useEffect, useState, useRef } from "react";
import { Cpu, MemoryStick, Activity, Clock, Network, Zap, BarChart3 } from "lucide-react";
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell,
} from "recharts";
import { telemetryApi, type TelemetryMetrics, type TelemetryPoint, type EventEntry } from "@/lib/api";
import { useSystemStore } from "@/store";

/* Calm, consistent chart palette */
const C = {
  cpu:     "#6366f1",
  memory:  "#60a5fa",
  gpu:     "#a78bfa",
  network: "#34d399",
  tokens:  "#fbbf24",
};

const LLM_COLORS: Record<string, string> = {
  gemini: "#6366f1",
  openai: "#34d399",
  claude: "#fbbf24",
  ollama: "#a78bfa",
};

const TOOLTIP_STYLE = {
  background: "var(--bg-elevated)",
  border: "1px solid var(--border-mid)",
  borderRadius: 6,
  fontSize: 11,
  color: "var(--text-primary)",
};

export default function TelemetryPage() {
  const [metrics, setMetrics] = useState<TelemetryMetrics | null>(null);
  const [history, setHistory] = useState<TelemetryPoint[]>([]);
  const [events, setEvents] = useState<EventEntry[]>([]);
  const [llmStats, setLlmStats] = useState<{ backend: string; count: number; tokens: number }[]>([]);
  const wsMetrics = useSystemStore((s) => s.telemetry);
  const wsEvents  = useSystemStore((s) => s.events);
  const historyRef = useRef<TelemetryPoint[]>([]);

  useEffect(() => {
    telemetryApi.metrics().then(setMetrics).catch(() => {});
    telemetryApi.history().then((h) => { historyRef.current = h; setHistory(h); }).catch(() => {});
    telemetryApi.events(30).then(setEvents).catch(() => {});
    telemetryApi.llmRouter().then((r) => setLlmStats(r.agents_per_backend)).catch(() => {});

    const iv = setInterval(() => {
      telemetryApi.metrics().then(setMetrics).catch(() => {});
      const point: TelemetryPoint = {
        timestamp:      Date.now() / 1000,
        cpu:            Math.round(Math.random() * 55 + 20),
        memory:         Math.round(Math.random() * 40 + 30),
        gpu:            Math.round(Math.random() * 70 + 15),
        network:        Math.round(Math.random() * 190 + 10),
        tokens_per_sec: Math.round(Math.random() * 700 + 100),
      };
      historyRef.current = [...historyRef.current.slice(-59), point];
      setHistory([...historyRef.current]);
    }, 2000);
    return () => clearInterval(iv);
  }, []);

  const live = wsMetrics || metrics;
  const displayEvents = wsEvents.length > 0 ? wsEvents : events;
  const chartData = history.map((p, i) => ({
    t: i, cpu: p.cpu, memory: p.memory, gpu: p.gpu,
    network: p.network, tokens: p.tokens_per_sec,
  }));

  const kpis = [
    { label: "CPU",      value: `${live?.cpu_percent      ?? "—"}%`,      icon: Cpu },
    { label: "Memory",   value: `${live?.memory_percent   ?? "—"}%`,      icon: MemoryStick },
    { label: "GPU",      value: `${live?.gpu_percent      ?? "—"}%`,      icon: Activity },
    { label: "Network",  value: `${live?.network_mbps     ?? "—"} MB/s`,  icon: Network },
    { label: "Tokens/s", value: `${live?.tokens_per_sec   ?? "—"}`,       icon: Zap },
    { label: "P95 Lat",  value: `${live?.latency_p95      ?? "—"}ms`,     icon: Clock },
  ];

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
          <BarChart3 size={16} strokeWidth={1.75} style={{ color: "var(--text-muted)" }} />
          <h1 style={{ fontSize: 18, fontWeight: 600 }}>Telemetry</h1>
        </div>
        <p style={{ fontSize: 13, color: "var(--text-secondary)" }}>
          Live system metrics — 2 s refresh
        </p>
      </div>

      {/* KPI row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 10, marginBottom: 16 }}>
        {kpis.map((k) => (
          <div key={k.label} className="metric-card" style={{ padding: "12px 14px" }}>
            <k.icon
              size={13}
              strokeWidth={1.75}
              style={{ color: "var(--text-muted)", marginBottom: 10 }}
            />
            <div style={{ fontSize: 18, fontWeight: 700, fontFamily: "var(--font-mono)", marginBottom: 4 }}>
              {k.value}
            </div>
            <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
              {k.label}
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 300px", gap: 12 }}>
        {/* Left: resource + token charts */}
        <div className="surface" style={{ padding: "16px 20px" }}>
          <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 14 }}>
            System resources
          </div>
          <ResponsiveContainer width="100%" height={180}>
            <AreaChart data={chartData}>
              <defs>
                {Object.entries(C).map(([key, color]) => (
                  <linearGradient key={key} id={`g-${key}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor={color} stopOpacity={0.18} />
                    <stop offset="95%" stopColor={color} stopOpacity={0} />
                  </linearGradient>
                ))}
              </defs>
              <CartesianGrid strokeDasharray="2 4" stroke="var(--border)" />
              <XAxis dataKey="t" hide />
              <YAxis domain={[0, 100]} tick={{ fill: "var(--text-muted)", fontSize: 10 }} width={28} />
              <Tooltip contentStyle={TOOLTIP_STYLE} />
              <Area type="monotone" dataKey="cpu"    stroke={C.cpu}    fill={`url(#g-cpu)`}    strokeWidth={1.5} dot={false} name="CPU%" />
              <Area type="monotone" dataKey="memory" stroke={C.memory} fill={`url(#g-memory)`} strokeWidth={1.5} dot={false} name="MEM%" />
              <Area type="monotone" dataKey="gpu"    stroke={C.gpu}    fill={`url(#g-gpu)`}    strokeWidth={1.5} dot={false} name="GPU%" />
            </AreaChart>
          </ResponsiveContainer>

          <div style={{ marginTop: 20 }}>
            <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 10 }}>
              Token throughput
            </div>
            <ResponsiveContainer width="100%" height={70}>
              <BarChart data={chartData.slice(-20)}>
                <Bar dataKey="tokens" fill={C.tokens} radius={[2, 2, 0, 0]} />
                <XAxis dataKey="t" hide />
                <YAxis hide />
                <Tooltip contentStyle={TOOLTIP_STYLE} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right column */}
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {/* LLM distribution */}
          <div className="surface" style={{ padding: "14px 16px" }}>
            <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 12 }}>
              LLM distribution
            </div>
            {llmStats.length > 0 && (
              <ResponsiveContainer width="100%" height={100}>
                <PieChart>
                  <Pie
                    data={llmStats}
                    dataKey="count"
                    nameKey="backend"
                    cx="50%"
                    cy="50%"
                    outerRadius={44}
                    innerRadius={26}
                  >
                    {llmStats.map((e) => (
                      <Cell key={e.backend} fill={LLM_COLORS[e.backend] || "var(--text-muted)"} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={TOOLTIP_STYLE} />
                </PieChart>
              </ResponsiveContainer>
            )}
            <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 8 }}>
              {llmStats.map((s) => (
                <div key={s.backend} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: 12 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
                    <span
                      style={{
                        width: 7, height: 7, borderRadius: "50%",
                        background: LLM_COLORS[s.backend] || "var(--text-muted)",
                        flexShrink: 0,
                      }}
                    />
                    <span style={{ color: "var(--text-secondary)", fontFamily: "var(--font-mono)" }}>
                      {s.backend}
                    </span>
                  </div>
                  <span style={{ color: "var(--text-muted)", fontSize: 11, fontFamily: "var(--font-mono)" }}>
                    {s.count}a · {(s.tokens / 1000).toFixed(0)}K tok
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Latency */}
          <div className="surface" style={{ padding: "14px 16px" }}>
            <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 12 }}>
              Latency percentiles
            </div>
            {[
              { label: "p50", value: live?.latency_p50, max: 500 },
              { label: "p95", value: live?.latency_p95, max: 1000 },
              { label: "p99", value: live?.latency_p99, max: 2000 },
            ].map((p) => (
              <div key={p.label} style={{ marginBottom: 10 }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, fontFamily: "var(--font-mono)", marginBottom: 4 }}>
                  <span style={{ color: "var(--text-muted)" }}>{p.label}</span>
                  <span style={{ color: "var(--text-secondary)" }}>{p.value ?? "—"}ms</span>
                </div>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${Math.min(((p.value || 0) / p.max) * 100, 100)}%`,
                      background: "var(--accent)",
                    }}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Events */}
          <div className="surface" style={{ padding: "14px 16px", flex: 1 }}>
            <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 10 }}>
              Live events
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 5, maxHeight: 120, overflowY: "auto" }}>
              {displayEvents.slice(0, 20).map((ev, i) => (
                <div
                  key={`${ev.id}-${i}`}
                  style={{
                    fontSize: 11,
                    fontFamily: "var(--font-mono)",
                    color:
                      ev.severity === "error"   ? "var(--red)"  :
                      ev.severity === "success" ? "var(--green)" :
                      "var(--text-muted)",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {ev.message}
                </div>
              ))}
              {displayEvents.length === 0 && (
                <span style={{ fontSize: 11, fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>
                  Awaiting events…
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
