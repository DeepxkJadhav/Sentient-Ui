"use client";
import { useEffect, useState } from "react";
import { Globe, Lock, Shield, Activity } from "lucide-react";
import { federationApi, type FederationNode, type EventEntry } from "@/lib/api";

export default function FederationPage() {
  const [nodes,       setNodes]       = useState<FederationNode[]>([]);
  const [audit,       setAudit]       = useState<EventEntry[]>([]);
  const [trustMatrix, setTrustMatrix] = useState<Record<string, Record<string, number>>>({});
  const [selected,    setSelected]    = useState<FederationNode | null>(null);

  useEffect(() => {
    federationApi.list().then(setNodes).catch(() => {});
    federationApi.auditTrail().then(setAudit).catch(() => {});
    federationApi.trustMatrix().then(setTrustMatrix).catch(() => {});
    const iv = setInterval(() => {
      federationApi.list().then(setNodes).catch(() => {});
      federationApi.auditTrail().then(setAudit).catch(() => {});
    }, 5000);
    return () => clearInterval(iv);
  }, []);

  const online      = nodes.filter((n) => n.status === "online").length;
  const totalAgents = nodes.reduce((s, n) => s + n.agents_count, 0);
  const avgTrust    = nodes.length
    ? ((nodes.reduce((s, n) => s + n.trust_score, 0) / nodes.length) * 100).toFixed(0)
    : "—";

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
          <Globe size={16} strokeWidth={1.75} style={{ color: "var(--text-muted)" }} />
          <h1 style={{ fontSize: 18, fontWeight: 600 }}>Federation</h1>
        </div>
        <p style={{ fontSize: 13, color: "var(--text-secondary)" }}>
          {online}/{nodes.length} nodes online
        </p>
      </div>

      {/* Summary row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10, marginBottom: 20 }}>
        {[
          { label: "Active nodes",      value: online,       icon: Globe },
          { label: "Federated agents",  value: totalAgents,  icon: Activity },
          { label: "Encrypted channels",value: nodes.filter((n) => n.encrypted).length, icon: Lock },
          { label: "Avg trust score",   value: `${avgTrust}%`, icon: Shield },
        ].map((item) => (
          <div key={item.label} className="metric-card">
            <item.icon size={13} strokeWidth={1.75} style={{ color: "var(--text-muted)", marginBottom: 10 }} />
            <div style={{ fontSize: 22, fontWeight: 700, marginBottom: 4 }}>{item.value}</div>
            <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{item.label}</div>
          </div>
        ))}
      </div>

      {/* Main grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 280px", gap: 12 }}>
        {/* Node list */}
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {nodes.map((node) => {
            const isSelected = selected?.id === node.id;
            return (
              <div
                key={node.id}
                className={`card ${isSelected ? "selected" : ""}`}
                style={{ padding: "14px 16px", cursor: "pointer" }}
                onClick={() => setSelected(node.id === selected?.id ? null : node)}
              >
                <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
                  <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
                    <span className={`status-dot status-${node.status}`} style={{ marginTop: 5 }} />
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 2 }}>
                        <span style={{ fontSize: 13, fontWeight: 600 }}>{node.name}</span>
                        {node.encrypted && (
                          <Lock size={11} strokeWidth={1.75} style={{ color: "var(--text-muted)" }} />
                        )}
                      </div>
                      <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                        {node.location} · {node.region}
                      </div>
                    </div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontSize: 12, fontWeight: 600, color: node.status === "online" ? "var(--green)" : node.status === "degraded" ? "var(--amber)" : "var(--red)" }}>
                      {node.status.charAt(0).toUpperCase() + node.status.slice(1)}
                    </div>
                    <div style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                      {node.latency_ms.toFixed(0)}ms
                    </div>
                  </div>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 8, marginTop: 12 }}>
                  {[
                    { label: "Trust",   value: `${(node.trust_score * 100).toFixed(0)}%` },
                    { label: "Agents",  value: node.agents_count },
                    { label: "Latency", value: `${node.latency_ms.toFixed(0)}ms` },
                  ].map((m) => (
                    <div key={m.label} style={{ textAlign: "center" }}>
                      <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 3 }}>
                        {m.label}
                      </div>
                      <div style={{ fontSize: 13, fontWeight: 600, fontFamily: "var(--font-mono)" }}>
                        {m.value}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="progress-bar" style={{ marginTop: 10 }}>
                  <div
                    className="progress-fill"
                    style={{
                      width: `${node.trust_score * 100}%`,
                      background: node.trust_score > 0.9 ? "var(--green)" : node.trust_score > 0.7 ? "var(--accent)" : "var(--amber)",
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        {/* Right column */}
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {/* Audit trail */}
          <div className="surface" style={{ padding: "14px 16px" }}>
            <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 10 }}>
              Audit trail
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 5, maxHeight: 240, overflowY: "auto", fontFamily: "var(--font-mono)", fontSize: 11 }}>
              {audit.map((ev, i) => (
                <div
                  key={`${ev.id}-${i}`}
                  style={{
                    display: "flex",
                    gap: 6,
                    color:
                      ev.severity === "success" ? "var(--green)"  :
                      ev.severity === "error"   ? "var(--red)"    :
                      "var(--text-muted)",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  <span style={{ flexShrink: 0 }}>
                    {ev.severity === "success" ? "✓" : ev.severity === "error" ? "✗" : "·"}
                  </span>
                  <span style={{ color: "var(--text-secondary)", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {ev.message}
                  </span>
                </div>
              ))}
              {audit.length === 0 && (
                <span style={{ color: "var(--text-muted)" }}>Awaiting events…</span>
              )}
            </div>
          </div>

          {/* Trust matrix */}
          {Object.keys(trustMatrix).length > 0 && (
            <div className="surface" style={{ padding: "14px 16px", overflowX: "auto" }}>
              <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 10 }}>
                Trust matrix
              </div>
              <table style={{ width: "100%", fontSize: 10, fontFamily: "var(--font-mono)", borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    <th style={{ textAlign: "left", color: "var(--text-muted)", paddingBottom: 6 }} />
                    {Object.keys(trustMatrix).slice(0, 4).map((name) => (
                      <th key={name} style={{ color: "var(--text-muted)", paddingBottom: 6, textAlign: "center", fontWeight: 500 }}>
                        {name.split(" ")[0]}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(trustMatrix).slice(0, 4).map(([row, cols]) => (
                    <tr key={row}>
                      <td style={{ color: "var(--text-muted)", paddingRight: 8, paddingBottom: 4 }}>
                        {row.split(" ")[0]}
                      </td>
                      {Object.entries(cols).slice(0, 4).map(([col, score]) => (
                        <td
                          key={col}
                          style={{
                            textAlign: "center",
                            paddingBottom: 4,
                            color:
                              score > 0.9  ? "var(--green)"  :
                              score > 0.7  ? "var(--accent)" :
                              "var(--red)",
                          }}
                        >
                          {(score * 100).toFixed(0)}%
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
