"use client";
import { useEffect, useState } from "react";
import { Cpu, MemoryStick, Activity, Wifi, WifiOff } from "lucide-react";
import { useSystemStore, useAgentStore } from "@/store";
import { useWebSocket } from "@/lib/useWebSocket";
import { systemApi, agentsApi } from "@/lib/api";

export default function TopBar() {
  useWebSocket();

  const telemetry = useSystemStore((s) => s.telemetry);
  const wsConnected = useSystemStore((s) => s.wsConnected);
  const setBackendOnline = useSystemStore((s) => s.setBackendOnline);
  const setAgents = useAgentStore((s) => s.setAgents);
  const [timeStr, setTimeStr] = useState("");

  useEffect(() => {
    const update = () =>
      setTimeStr(
        new Date().toISOString().replace("T", " ").substring(0, 19) + " UTC"
      );
    update();
    const iv = setInterval(update, 1000);
    return () => clearInterval(iv);
  }, []);

  useEffect(() => {
    agentsApi.list().then(setAgents).catch(() => {});
    systemApi
      .health()
      .then(() => setBackendOnline(true))
      .catch(() => setBackendOnline(false));
  }, []);

  return (
    <header
      style={{
        height: 44,
        flexShrink: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 24px",
        borderBottom: "1px solid var(--border)",
        background: "var(--bg-surface)",
      }}
    >
      {/* Left: timestamp */}
      <span
        suppressHydrationWarning
        style={{
          fontSize: 12,
          fontFamily: "var(--font-mono)",
          color: "var(--text-muted)",
        }}
      >
        {timeStr}
      </span>

      {/* Right: live metrics + connection */}
      <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
        <Metric icon={<Cpu size={12} />} label="CPU" value={`${telemetry?.cpu_percent ?? "—"}%`} />
        <Metric icon={<MemoryStick size={12} />} label="MEM" value={`${telemetry?.memory_percent ?? "—"}%`} />
        <Metric icon={<Activity size={12} />} label="GPU" value={`${telemetry?.gpu_percent ?? "—"}%`} />

        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          {wsConnected ? (
            <Wifi size={12} style={{ color: "var(--green)" }} />
          ) : (
            <WifiOff size={12} style={{ color: "var(--red)" }} />
          )}
          <span
            style={{
              fontSize: 12,
              fontFamily: "var(--font-mono)",
              color: wsConnected ? "var(--green)" : "var(--red)",
            }}
          >
            {wsConnected ? "Live" : "Offline"}
          </span>
        </div>
      </div>
    </header>
  );
}

function Metric({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 5,
        fontSize: 12,
        fontFamily: "var(--font-mono)",
        color: "var(--text-secondary)",
      }}
    >
      <span style={{ color: "var(--text-muted)" }}>{icon}</span>
      <span style={{ color: "var(--text-muted)" }}>{label}</span>
      <span style={{ color: "var(--text-primary)" }}>{value}</span>
    </div>
  );
}
