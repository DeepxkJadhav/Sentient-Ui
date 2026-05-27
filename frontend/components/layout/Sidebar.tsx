"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Bot, Network, Brain, Target,
  Globe, BarChart3, Puzzle, Settings,
} from "lucide-react";
import { useAgentStore, useSystemStore } from "@/store";

const NAV = [
  { href: "/",           icon: LayoutDashboard, label: "Dashboard" },
  { href: "/agents",     icon: Bot,             label: "Agents" },
  { href: "/swarm",      icon: Network,         label: "Swarm" },
  { href: "/memory",     icon: Brain,           label: "Memory" },
  { href: "/goals",      icon: Target,          label: "Goals" },
  { href: "/federation", icon: Globe,           label: "Federation" },
  { href: "/telemetry",  icon: BarChart3,       label: "Telemetry" },
  { href: "/plugins",    icon: Puzzle,          label: "Plugins" },
];

const BOTTOM_NAV = [
  { href: "/settings",   icon: Settings,        label: "Settings" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const agents = useAgentStore((s) => s.agents);
  const wsConnected = useSystemStore((s) => s.wsConnected);

  const activeCount = agents.filter(
    (a) => a.status === "executing" || a.status === "thinking"
  ).length;

  return (
    <aside
      style={{
        width: 220,
        flexShrink: 0,
        display: "flex",
        flexDirection: "column",
        borderRight: "1px solid var(--border)",
        background: "var(--bg-surface)",
      }}
    >
      {/* Wordmark */}
      <div
        style={{
          padding: "20px 18px 16px",
          borderBottom: "1px solid var(--border)",
        }}
      >
        <div style={{ fontSize: 14, fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.01em" }}>
          Sentient
        </div>
        <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
          v1.0 · Alpha
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: "10px 8px", overflowY: "auto" }}>
        <div className="section-label" style={{ padding: "8px 10px 6px" }}>
          Navigation
        </div>

        {NAV.map(({ href, icon: Icon, label }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`sidebar-item ${active ? "active" : ""}`}
            >
              <Icon size={14} strokeWidth={1.75} />
              <span>{label}</span>
              {href === "/agents" && activeCount > 0 && (
                <span
                  className="badge badge-accent"
                  style={{ marginLeft: "auto", fontSize: 10, padding: "1px 6px" }}
                >
                  {activeCount}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Bottom nav */}
      <nav style={{ padding: "4px 8px" }}>
        {BOTTOM_NAV.map(({ href, icon: Icon, label }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`sidebar-item ${active ? "active" : ""}`}
            >
              <Icon size={14} strokeWidth={1.75} />
              <span>{label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Status footer */}
      <div
        style={{
          padding: "12px 14px",
          borderTop: "1px solid var(--border)",
          display: "flex",
          alignItems: "center",
          gap: 8,
        }}
      >
        <span
          className={`status-dot ${wsConnected ? "status-online" : "status-error"}`}
        />
        <span style={{ fontSize: 12, color: "var(--text-secondary)" }}>
          {wsConnected ? "Connected" : "Disconnected"}
        </span>
      </div>
    </aside>
  );
}
