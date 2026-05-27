"use client";
import { useEffect, useState } from "react";
import { Bot, Plus, RefreshCw, FileText, X } from "lucide-react";
import { useAgentStore } from "@/store";
import { agentsApi, type Agent, type EventEntry } from "@/lib/api";

const LLM_OPTIONS = ["gemini", "openai", "claude", "ollama"];
const ROLE_OPTIONS = [
  "Code Architect",
  "Backend Engineer",
  "Frontend Engineer",
  "Security Auditor",
  "DevOps Agent",
  "ML Engineer",
  "Testing Agent",
  "Planner Agent",
  "Research Agent",
  "Documentation Agent",
  "Debugging Agent",
  "Database Optimizer",
  "Custom Agent",
];

const STATUS_LABEL: Record<string, string> = {
  idle:      "Idle",
  thinking:  "Thinking",
  executing: "Executing",
  error:     "Error",
  offline:   "Offline",
};

export default function AgentsPage() {
  const agents = useAgentStore((s) => s.agents);
  const setAgents = useAgentStore((s) => s.setAgents);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [logs, setLogs] = useState<EventEntry[]>([]);
  const [spawning, setSpawning] = useState(false);
  const [form, setForm] = useState({
    name: "",
    role: ROLE_OPTIONS[0],
    llm_backend: "gemini",
    icon: "🤖",
  });

  const refresh = () => agentsApi.list().then(setAgents).catch(() => {});

  useEffect(() => {
    refresh();
  }, []);

  useEffect(() => {
    if (!selectedAgent) return;
    agentsApi.logs(selectedAgent.id).then(setLogs).catch(() => {});
    const iv = setInterval(() => {
      if (selectedAgent)
        agentsApi.logs(selectedAgent.id).then(setLogs).catch(() => {});
    }, 3000);
    return () => clearInterval(iv);
  }, [selectedAgent?.id]);

  const handleSpawn = async () => {
    if (!form.name.trim()) return;
    setSpawning(false);
    const agent = await agentsApi.create(form);
    setAgents([...agents, agent]);
  };

  const handleRestart = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    await agentsApi.restart(id);
    refresh();
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          marginBottom: 24,
        }}
      >
        <div>
          <h1 style={{ fontSize: 18, fontWeight: 600, marginBottom: 4 }}>Agents</h1>
          <p style={{ fontSize: 13, color: "var(--text-secondary)" }}>
            {agents.length} registered ·{" "}
            {agents.filter((a) => a.status === "executing").length} executing ·{" "}
            {agents.filter((a) => a.status === "thinking").length} thinking
          </p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn btn-ghost" onClick={refresh}>
            <RefreshCw size={13} strokeWidth={1.75} />
            Refresh
          </button>
          <button className="btn btn-primary" onClick={() => setSpawning(true)}>
            <Plus size={13} strokeWidth={1.75} />
            New agent
          </button>
        </div>
      </div>

      {/* Two-column layout */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 300px", gap: 12 }}>
        {/* Agent grid */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(2, 1fr)",
            gap: 8,
            alignContent: "start",
          }}
        >
          {agents.map((agent) => (
            <div
              key={agent.id}
              className={`agent-card ${selectedAgent?.id === agent.id ? "selected" : ""}`}
              style={{ padding: "14px 16px" }}
              onClick={() =>
                setSelectedAgent(agent.id === selectedAgent?.id ? null : agent)
              }
            >
              {/* Name + status */}
              <div
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  justifyContent: "space-between",
                  marginBottom: 8,
                }}
              >
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600 }}>{agent.name}</div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 1 }}>
                    {agent.role}
                  </div>
                </div>
                <span className={`status-dot status-${agent.status}`} />
              </div>

              {/* Task */}
              <div
                style={{
                  fontSize: 12,
                  color: "var(--text-muted)",
                  fontFamily: "var(--font-mono)",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                  marginBottom: 10,
                }}
              >
                {agent.current_task || STATUS_LABEL[agent.status] || agent.status}
              </div>

              {/* Metrics row */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(3, 1fr)",
                  gap: 4,
                  marginBottom: 10,
                }}
              >
                {[
                  { label: "CPU", val: `${agent.cpu_percent}%` },
                  { label: "RAM", val: `${Math.round(agent.memory_mb)}M` },
                  { label: "Lat", val: `${Math.round(agent.latency_ms)}ms` },
                ].map((m) => (
                  <div key={m.label} style={{ textAlign: "center" }}>
                    <div
                      style={{
                        fontSize: 10,
                        color: "var(--text-muted)",
                        textTransform: "uppercase",
                        letterSpacing: "0.06em",
                      }}
                    >
                      {m.label}
                    </div>
                    <div
                      style={{
                        fontSize: 12,
                        fontFamily: "var(--font-mono)",
                        color: "var(--text-secondary)",
                      }}
                    >
                      {m.val}
                    </div>
                  </div>
                ))}
              </div>

              {/* Footer */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <span className="badge badge-muted" style={{ fontSize: 10 }}>
                    {agent.llm_backend}
                  </span>
                  {agent.is_llm_real && (
                    <span className="badge badge-green" style={{ fontSize: 10 }}>
                      ⚡ Live
                    </span>
                  )}
                </div>
                <button
                  style={{
                    fontSize: 11,
                    color: "var(--text-muted)",
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    fontFamily: "var(--font-sans)",
                    padding: "2px 0",
                  }}
                  onMouseEnter={(e) =>
                    (e.currentTarget.style.color = "var(--text-primary)")
                  }
                  onMouseLeave={(e) =>
                    (e.currentTarget.style.color = "var(--text-muted)")
                  }
                  onClick={(e) => handleRestart(agent.id, e)}
                >
                  Restart
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Log panel */}
        <div
          className="surface"
          style={{
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            maxHeight: "calc(100vh - 160px)",
          }}
        >
          {selectedAgent ? (
            <>
              {/* Log header */}
              <div
                style={{
                  padding: "12px 16px",
                  borderBottom: "1px solid var(--border)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <FileText size={13} strokeWidth={1.75} style={{ color: "var(--text-muted)" }} />
                  <span style={{ fontSize: 13, fontWeight: 500 }}>{selectedAgent.name}</span>
                </div>
                <button
                  onClick={() => setSelectedAgent(null)}
                  style={{
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    color: "var(--text-muted)",
                    display: "flex",
                  }}
                >
                  <X size={13} />
                </button>
              </div>

              {/* Stats */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: 8,
                  padding: "12px 16px",
                  borderBottom: "1px solid var(--border)",
                }}
              >
                <div>
                  <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 4 }}>
                    Tokens
                  </div>
                  <div style={{ fontSize: 16, fontWeight: 700, fontFamily: "var(--font-mono)" }}>
                    {selectedAgent.tokens_used.toLocaleString()}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 4 }}>
                    Tasks done
                  </div>
                  <div style={{ fontSize: 16, fontWeight: 700, fontFamily: "var(--font-mono)" }}>
                    {selectedAgent.tasks_completed}
                  </div>
                </div>
              </div>

              {/* Last LLM output */}
              {selectedAgent.last_llm_output && (
                <div
                  style={{
                    padding: "10px 16px",
                    borderBottom: "1px solid var(--border)",
                  }}
                >
                  <div
                    style={{
                      fontSize: 10,
                      color: selectedAgent.is_llm_real ? "var(--green)" : "var(--text-muted)",
                      textTransform: "uppercase",
                      letterSpacing: "0.06em",
                      marginBottom: 6,
                      display: "flex",
                      alignItems: "center",
                      gap: 5,
                    }}
                  >
                    {selectedAgent.is_llm_real ? "⚡ Real LLM Output" : "● Simulated Task"}
                  </div>
                  <div
                    style={{
                      fontSize: 12,
                      fontFamily: "var(--font-mono)",
                      color: "var(--text-secondary)",
                      lineHeight: 1.6,
                      background: "var(--bg-elevated)",
                      borderRadius: "var(--radius)",
                      padding: "8px 10px",
                      border: selectedAgent.is_llm_real
                        ? "1px solid rgba(52,211,153,0.25)"
                        : "1px solid var(--border)",
                    }}
                  >
                    {selectedAgent.last_llm_output}
                  </div>
                </div>
              )}

              {/* Logs */}
              <div
                style={{
                  flex: 1,
                  overflowY: "auto",
                  padding: "12px 16px",
                  display: "flex",
                  flexDirection: "column",
                  gap: 5,
                  fontFamily: "var(--font-mono)",
                  fontSize: 11,
                }}
              >
                {logs.map((log, i) => (
                  <div
                    key={`${log.id}-${i}`}
                    style={{ display: "flex", gap: 8, alignItems: "flex-start" }}
                  >
                    <span style={{ color: "var(--text-muted)", flexShrink: 0 }}>
                      {new Date(log.ts).toLocaleTimeString()}
                    </span>
                    <span
                      style={{
                        color:
                          log.severity === "error"
                            ? "var(--red)"
                            : log.severity === "success"
                            ? "var(--green)"
                            : "var(--text-secondary)",
                      }}
                    >
                      {log.message}
                    </span>
                  </div>
                ))}
                {logs.length === 0 && (
                  <span style={{ color: "var(--text-muted)" }}>No logs yet</span>
                )}
              </div>
            </>
          ) : (
            <div
              style={{
                flex: 1,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                gap: 8,
                color: "var(--text-muted)",
                padding: 24,
                textAlign: "center",
              }}
            >
              <FileText size={24} strokeWidth={1.25} />
              <span style={{ fontSize: 13 }}>Select an agent to view its logs</span>
            </div>
          )}
        </div>
      </div>

      {/* Spawn modal */}
      {spawning && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.6)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 50,
          }}
          onClick={() => setSpawning(false)}
        >
          <div
            style={{
              background: "var(--bg-elevated)",
              border: "1px solid var(--border-mid)",
              borderRadius: "var(--radius-lg)",
              padding: 24,
              width: 380,
              display: "flex",
              flexDirection: "column",
              gap: 16,
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ fontSize: 15, fontWeight: 600 }}>New agent</div>

            <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              <span style={{ fontSize: 12, color: "var(--text-muted)" }}>Name</span>
              <input
                className="sentient-input"
                placeholder="e.g. Nova"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
            </label>

            <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              <span style={{ fontSize: 12, color: "var(--text-muted)" }}>Role</span>
              <select
                className="sentient-input"
                value={form.role}
                onChange={(e) => setForm({ ...form, role: e.target.value })}
              >
                {ROLE_OPTIONS.map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>
            </label>

            <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              <span style={{ fontSize: 12, color: "var(--text-muted)" }}>LLM backend</span>
              <select
                className="sentient-input"
                value={form.llm_backend}
                onChange={(e) => setForm({ ...form, llm_backend: e.target.value })}
              >
                {LLM_OPTIONS.map((l) => (
                  <option key={l} value={l}>
                    {l}
                  </option>
                ))}
              </select>
            </label>

            <div style={{ display: "flex", gap: 8, marginTop: 4 }}>
              <button className="btn btn-ghost" style={{ flex: 1 }} onClick={() => setSpawning(false)}>
                Cancel
              </button>
              <button className="btn btn-primary" style={{ flex: 1 }} onClick={handleSpawn}>
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

