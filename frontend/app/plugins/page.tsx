"use client";
import { useEffect } from "react";
import { Puzzle, Star, Download, ToggleLeft, ToggleRight } from "lucide-react";
import { usePluginStore } from "@/store";
import { pluginsApi } from "@/lib/api";

export default function PluginsPage() {
  const plugins      = usePluginStore((s) => s.plugins);
  const setPlugins   = usePluginStore((s) => s.setPlugins);
  const togglePlugin = usePluginStore((s) => s.togglePlugin);

  useEffect(() => {
    pluginsApi.list().then(setPlugins).catch(() => {});
  }, []);

  const handleToggle = async (id: string) => {
    togglePlugin(id);
    await pluginsApi.toggle(id).catch(() => togglePlugin(id));
  };

  const categories = [...new Set(plugins.map((p) => p.category))];

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
          <Puzzle size={16} strokeWidth={1.75} style={{ color: "var(--text-muted)" }} />
          <h1 style={{ fontSize: 18, fontWeight: 600 }}>Plugins</h1>
        </div>
        <p style={{ fontSize: 13, color: "var(--text-secondary)" }}>
          {plugins.filter((p) => p.enabled).length}/{plugins.length} enabled
        </p>
      </div>

      {/* Category summary */}
      <div style={{ display: "flex", gap: 8, marginBottom: 20, flexWrap: "wrap" }}>
        {categories.map((cat) => {
          const count   = plugins.filter((p) => p.category === cat).length;
          const enabled = plugins.filter((p) => p.category === cat && p.enabled).length;
          return (
            <div
              key={cat}
              className="metric-card"
              style={{ padding: "10px 14px", display: "flex", alignItems: "center", gap: 10 }}
            >
              <div style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--accent)", flexShrink: 0 }} />
              <div>
                <div style={{ fontSize: 12, fontWeight: 500, textTransform: "capitalize" }}>{cat}</div>
                <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{enabled}/{count}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Plugin grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 10 }}>
        {plugins.map((plugin) => (
          <div
            key={plugin.id}
            className="card"
            style={{ padding: "16px 18px", opacity: plugin.enabled ? 1 : 0.5 }}
          >
            {/* Header row */}
            <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 10 }}>
              <div>
                <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 2 }}>
                  {plugin.name}
                </div>
                <div style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                  v{plugin.version} · {plugin.author}
                </div>
              </div>
              <button
                onClick={() => handleToggle(plugin.id)}
                style={{
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  color: plugin.enabled ? "var(--accent)" : "var(--text-muted)",
                  display: "flex",
                  flexShrink: 0,
                  transition: "color 0.14s ease",
                }}
              >
                {plugin.enabled
                  ? <ToggleRight size={22} strokeWidth={1.75} />
                  : <ToggleLeft  size={22} strokeWidth={1.75} />
                }
              </button>
            </div>

            {/* Description */}
            <p
              style={{
                fontSize: 13,
                color: "var(--text-secondary)",
                marginBottom: 12,
                display: "-webkit-box",
                WebkitLineClamp: 2,
                WebkitBoxOrient: "vertical",
                overflow: "hidden",
              }}
            >
              {plugin.description}
            </p>

            {/* Footer */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <span className="badge badge-muted" style={{ textTransform: "capitalize" }}>
                {plugin.category}
              </span>

              <div style={{ display: "flex", alignItems: "center", gap: 12, fontSize: 11, color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                  <Star size={10} strokeWidth={1.75} />
                  {plugin.rating}
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                  <Download size={10} strokeWidth={1.75} />
                  {plugin.downloads.toLocaleString()}
                </div>
              </div>
            </div>

            <div style={{ marginTop: 10, paddingTop: 10, borderTop: "1px solid var(--border)" }}>
              <span
                className={`badge ${plugin.enabled ? "badge-green" : "badge-muted"}`}
                style={{ textTransform: "none" }}
              >
                {plugin.enabled ? "Active" : "Disabled"}
              </span>
            </div>
          </div>
        ))}
      </div>

      {plugins.length === 0 && (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: "56px 0",
            gap: 10,
            color: "var(--text-muted)",
          }}
        >
          <Puzzle size={24} strokeWidth={1.25} />
          <span style={{ fontSize: 13 }}>Loading plugin registry…</span>
        </div>
      )}
    </div>
  );
}
