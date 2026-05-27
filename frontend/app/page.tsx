"use client";
import { useEffect, useState } from "react";
import { Bot, Brain, Target, Network, Activity } from "lucide-react";
import { useAgentStore, useSystemStore } from "@/store";
import { systemApi, telemetryApi } from "@/lib/api";
import type { SystemOverview, EventEntry } from "@/lib/api";

const STATUS_COLOR: Record<string, string> = {
  idle:      "var(--text-muted)",
  thinking:  "var(--blue)",
  executing: "var(--green)",
  error:     "var(--red)",
  offline:   "var(--text-muted)",
};

export default function DashboardPage() {
  const agents = useAgentStore((s) => s.agents);
  const events = useSystemStore((s) => s.events);
  const [overview, setOverview] = useState<SystemOverview | null>(null);
  const [recentEvents, setRecentEvents] = useState<EventEntry[]>([]);

  useEffect(() => {
    systemApi.overview().then(setOverview).catch(() => {});
    telemetryApi.events(20).then(setRecentEvents).catch(() => {});
  }, []);

  const byStatus = {
    idle:      agents.filter((a) => a.status === "idle").length,
    thinking:  agents.filter((a) => a.status === "thinking").length,
    executing: agents.filter((a) => a.status === "executing").length,
    error:     agents.filter((a) => a.status === "error").length,
  };

  const displayEvents = [...events, ...recentEvents].slice(0, 15);

  const kpis = [
    {
      label: "Agents",
      value: agents.length || overview?.agents.total || 0,
      icon: Bot,
      sub: `${byStatus.executing} executing`,
    },
    {
      label: "Memory entries",
      value: overview?.memory.total || 0,
      icon: Brain,
      sub: "Shared vector store",
    },
    {
      label: "Active goals",
      value: overview?.goals.total || 0,
      icon: Target,
      sub: "In DAG planning",
    },
    {
      label: "Swarm channels",
      value: overview?.swarm.active_channels || 0,
      icon: Network,
      sub: `${overview?.swarm.messages_per_sec ?? 0} msg/s`,
    },
  ];

  const systemMetrics = [
    {
      label: "CPU",
      value: overview?.system.cpu_percent ?? 0,
      unit: "%",
    },
    {
      label: "Memory",
      value: overview?.system.memory_percent ?? 0,
      unit: "%",
    },
    {
      label: "GPU",
      value: overview?.system.gpu_percent ?? 0,
      unit: "%",
    },
    {
      label: "Uptime",
      value: Math.round((overview?.system.uptime_seconds ?? 0) / 3600),
      unit: "h",
    },
  ];

  return (
    <div className="page-container">
      {/* Page header */}
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 18, fontWeight: 600, color: "var(--text-primary)", marginBottom: 4 }}>
          Dashboard
        </h1>
        <p style={{ fontSize: 13, color: "var(--text-secondary)" }}>
          Multi-agent orchestration overview
        </p>
      </div>

      {/* KPI row */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 12,
          marginBottom: 20,
        }}
      >
        {kpis.map((kpi) => (
          <div key={kpi.label} className="metric-card">
            <kpi.icon
              size={14}
              strokeWidth={1.75}
              style={{ color: "var(--text-muted)", marginBottom: 12 }}
            />
            <div
              style={{
                fontSize: 24,
                fontWeight: 700,
                color: "var(--text-primary)",
                lineHeight: 1,
                marginBottom: 6,
              }}
            >
              {kpi.value}
            </div>
            <div style={{ fontSize: 13, color: "var(--text-primary)", fontWeight: 500 }}>
              {kpi.label}
            </div>
            <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>
              {kpi.sub}
            </div>
          </div>
        ))}
      </div>

      {/* Main two-column */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 320px", gap: 12, marginBottom: 12 }}>
        {/* Agent list */}
        <div className="surface" style={{ padding: "16px 20px" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: 14,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <Bot size={14} strokeWidth={1.75} style={{ color: "var(--text-secondary)" }} />
              <span style={{ fontSize: 13, fontWeight: 600 }}>Agent Runtime</span>
            </div>
            <span
              style={{
                fontSize: 12,
                color: "var(--text-muted)",
              }}
            >
              {agents.length} agents
            </span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 4, maxHeight: 260, overflowY: "auto" }}>
            {agents.slice(0, 12).map((agent) => (
              <div
                key={agent.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  padding: "8px 10px",
                  borderRadius: "var(--radius)",
                  background: "var(--bg-elevated)",
                }}
              >
                <span className={`status-dot status-${agent.status}`} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 13, fontWeight: 500 }}>{agent.name}</div>
                  <div
                    style={{
                      fontSize: 12,
                      color: "var(--text-muted)",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {agent.current_task || agent.role}
                  </div>
                </div>
                <span
                  style={{
                    fontSize: 11,
                    fontFamily: "var(--font-mono)",
                    color: "var(--text-muted)",
                    flexShrink: 0,
                  }}
                >
                  {agent.cpu_percent}%
                </span>
              </div>
            ))}
            {agents.length === 0 && (
              <div
                style={{
                  padding: "32px 0",
                  textAlign: "center",
                  color: "var(--text-muted)",
                  fontSize: 13,
                }}
              >
                Connecting to backend…
              </div>
            )}
          </div>
        </div>

        {/* Event stream */}
        <div className="surface" style={{ padding: "16px 18px", display: "flex", flexDirection: "column" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
            <Activity size={14} strokeWidth={1.75} style={{ color: "var(--text-secondary)" }} />
            <span style={{ fontSize: 13, fontWeight: 600 }}>Events</span>
          </div>

          <div
            style={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              gap: 6,
              overflowY: "auto",
              maxHeight: 260,
            }}
          >
            {displayEvents.map((ev, i) => (
              <div
                key={`${ev.id}-${i}`}
                style={{
                  display: "flex",
                  gap: 8,
                  fontSize: 12,
                  fontFamily: "var(--font-mono)",
                  alignItems: "flex-start",
                }}
              >
                <span
                  style={{
                    color:
                      ev.severity === "success"
                        ? "var(--green)"
                        : ev.severity === "error"
                        ? "var(--red)"
                        : "var(--text-muted)",
                    flexShrink: 0,
                  }}
                >
                  {ev.severity === "success" ? "✓" : ev.severity === "error" ? "✗" : "·"}
                </span>
                <span
                  style={{
                    color: "var(--text-secondary)",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {ev.message}
                </span>
              </div>
            ))}
            {displayEvents.length === 0 && (
              <span style={{ fontSize: 12, color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                Awaiting events…
              </span>
            )}
          </div>
        </div>
      </div>

      {/* System resource row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
        {systemMetrics.map((m) => (
          <div key={m.label} className="metric-card" style={{ padding: "14px 16px" }}>
            <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.06em" }}>
              {m.label}
            </div>
            <div
              style={{
                fontSize: 20,
                fontWeight: 700,
                fontFamily: "var(--font-mono)",
                color: "var(--text-primary)",
                marginBottom: m.unit !== "h" ? 8 : 0,
              }}
            >
              {m.value}{m.unit}
            </div>
            {m.unit !== "h" && (
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${m.value}%`, background: "var(--accent)" }}
                />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
