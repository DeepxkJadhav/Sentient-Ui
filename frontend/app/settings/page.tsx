"use client";
import { useEffect, useState, useCallback } from "react";
import {
  Settings, Key, CheckCircle, AlertCircle, Trash2,
  Eye, EyeOff, ExternalLink, ChevronDown, ChevronRight, Cpu, Save,
} from "lucide-react";
import {
  settingsApi,
  type Provider,
  type SettingsResponse,
  type SystemSettingsInput,
} from "@/lib/api";

/* ── category metadata ───────────────────────────────────────────────────── */
const CATEGORIES: { id: string; label: string; desc: string }[] = [
  { id: "llm",           label: "LLM providers",     desc: "AI model backends that power your agents" },
  { id: "developer",     label: "Developer tools",    desc: "Code repos, issue trackers, CI/CD" },
  { id: "google",        label: "Google services",    desc: "Gmail, Calendar, Drive, Sheets" },
  { id: "communication", label: "Communication",      desc: "Slack, Discord, Telegram, email" },
  { id: "productivity",  label: "Productivity",       desc: "Notion, Airtable, HubSpot" },
  { id: "cloud",         label: "Cloud & infra",      desc: "AWS, GCP, Azure" },
  { id: "business",      label: "Business",           desc: "Payments, analytics, data" },
  { id: "data",          label: "Data & search",      desc: "Web search, weather, market data" },
];

const LLM_OPTIONS = ["gemini", "openai", "claude", "ollama", "groq", "mistral"];

/* ── component ───────────────────────────────────────────────────────────── */
export default function SettingsPage() {
  const [providers, setProviders]   = useState<Provider[]>([]);
  const [settings, setSettings]     = useState<SettingsResponse | null>(null);
  const [draftKeys, setDraftKeys]   = useState<Record<string, string>>({});
  const [showKey, setShowKey]       = useState<Record<string, boolean>>({});
  const [saving, setSaving]         = useState<Record<string, boolean>>({});
  const [saved, setSaved]           = useState<Record<string, boolean>>({});
  const [error, setError]           = useState<Record<string, string>>({});
  const [openCats, setOpenCats]     = useState<Record<string, boolean>>({ llm: true });
  const [sysForm, setSysForm]       = useState<SystemSettingsInput>({});
  const [sysSaving, setSysSaving]   = useState(false);
  const [sysSaved, setSysSaved]     = useState(false);
  const [activeTab, setActiveTab]   = useState<"keys" | "system">("keys");

  const load = useCallback(async () => {
    const [prov, cfg] = await Promise.all([
      settingsApi.getProviders().catch(() => [] as Provider[]),
      settingsApi.get().catch(() => null),
    ]);
    setProviders(prov);
    setSettings(cfg);
    if (cfg?.system) {
      setSysForm({
        agent_tick_interval:  cfg.system.agent_tick_interval,
        max_agents:           cfg.system.max_agents,
        memory_retention_days: cfg.system.memory_retention_days,
        default_llm:          cfg.llm_routing?.default,
        fallback_llm:         cfg.llm_routing?.fallback,
      });
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleSaveKey = async (providerId: string) => {
    const key = draftKeys[providerId]?.trim();
    if (!key) return;
    setSaving((p) => ({ ...p, [providerId]: true }));
    setError((p) => ({ ...p, [providerId]: "" }));
    try {
      await settingsApi.setApiKey(providerId, key);
      setDraftKeys((p) => ({ ...p, [providerId]: "" }));
      setSaved((p) => ({ ...p, [providerId]: true }));
      setTimeout(() => setSaved((p) => ({ ...p, [providerId]: false })), 2500);
      await load();
    } catch (e: any) {
      setError((p) => ({ ...p, [providerId]: e.message || "Failed to save" }));
    } finally {
      setSaving((p) => ({ ...p, [providerId]: false }));
    }
  };

  const handleDeleteKey = async (providerId: string) => {
    try {
      await settingsApi.deleteApiKey(providerId);
      await load();
    } catch { /* ignore */ }
  };

  const handleSaveSystem = async () => {
    setSysSaving(true);
    try {
      await settingsApi.updateSystem(sysForm);
      setSysSaved(true);
      setTimeout(() => setSysSaved(false), 2500);
    } finally {
      setSysSaving(false);
    }
  };

  const toggleCat = (id: string) =>
    setOpenCats((p) => ({ ...p, [id]: !p[id] }));

  const byCategory = (catId: string) =>
    providers.filter((p) => p.category === catId);

  const isConfigured = (id: string) =>
    settings?.api_keys_configured.includes(id) ?? false;

  const maskedValue = (id: string) =>
    settings?.api_keys[id] ?? "";

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
          <Settings size={16} strokeWidth={1.75} style={{ color: "var(--text-muted)" }} />
          <h1 style={{ fontSize: 18, fontWeight: 600 }}>Settings</h1>
        </div>
        <p style={{ fontSize: 13, color: "var(--text-secondary)" }}>
          Configure API keys and system behaviour — saved to the backend
        </p>
      </div>

      {/* Tab bar */}
      <div
        style={{
          display: "flex",
          gap: 0,
          borderBottom: "1px solid var(--border)",
          marginBottom: 24,
        }}
      >
        {([
          { id: "keys",   label: "API keys" },
          { id: "system", label: "System config" },
        ] as const).map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              background: "none",
              border: "none",
              borderBottom: activeTab === tab.id
                ? "2px solid var(--accent)"
                : "2px solid transparent",
              padding: "8px 18px",
              fontSize: 13,
              fontWeight: 500,
              color: activeTab === tab.id ? "var(--accent)" : "var(--text-secondary)",
              cursor: "pointer",
              transition: "color 0.14s ease",
              marginBottom: -1,
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ── API KEYS TAB ─────────────────────────────────────────────────── */}
      {activeTab === "keys" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {/* Summary banner */}
          <div
            className="surface"
            style={{
              padding: "12px 18px",
              marginBottom: 8,
              display: "flex",
              alignItems: "center",
              gap: 12,
            }}
          >
            <Key size={14} strokeWidth={1.75} style={{ color: "var(--text-muted)" }} />
            <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>
              {settings?.api_keys_configured.length ?? 0} of {providers.length} providers configured
            </span>
            {settings && settings.api_keys_configured.length > 0 && (
              <div style={{ display: "flex", gap: 6, marginLeft: 8, flexWrap: "wrap" }}>
                {settings.api_keys_configured.slice(0, 6).map((id) => (
                  <span key={id} className="badge badge-green" style={{ textTransform: "none" }}>
                    {id}
                  </span>
                ))}
                {settings.api_keys_configured.length > 6 && (
                  <span className="badge badge-muted">
                    +{settings.api_keys_configured.length - 6}
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Category accordion */}
          {CATEGORIES.map((cat) => {
            const provs = byCategory(cat.id);
            if (provs.length === 0) return null;
            const configuredCount = provs.filter((p) => isConfigured(p.id)).length;
            const isOpen = openCats[cat.id] ?? false;

            return (
              <div key={cat.id} className="surface" style={{ overflow: "hidden" }}>
                {/* Accordion header */}
                <button
                  onClick={() => toggleCat(cat.id)}
                  style={{
                    width: "100%",
                    background: "none",
                    border: "none",
                    padding: "14px 18px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    cursor: "pointer",
                    textAlign: "left",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    {isOpen
                      ? <ChevronDown size={14} strokeWidth={1.75} style={{ color: "var(--text-muted)" }} />
                      : <ChevronRight size={14} strokeWidth={1.75} style={{ color: "var(--text-muted)" }} />
                    }
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)" }}>
                        {cat.label}
                      </div>
                      <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{cat.desc}</div>
                    </div>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
                    {configuredCount > 0 && (
                      <span className="badge badge-green">
                        {configuredCount}/{provs.length}
                      </span>
                    )}
                    <span className="badge badge-muted">{provs.length}</span>
                  </div>
                </button>

                {/* Provider rows */}
                {isOpen && (
                  <div style={{ borderTop: "1px solid var(--border)" }}>
                    {provs.map((prov, idx) => {
                      const configured = isConfigured(prov.id);
                      const draft = draftKeys[prov.id] ?? "";
                      const visible = showKey[prov.id] ?? false;
                      const isSaving = saving[prov.id];
                      const wasSaved = saved[prov.id];
                      const err = error[prov.id];

                      return (
                        <div
                          key={prov.id}
                          style={{
                            padding: "14px 18px",
                            borderBottom:
                              idx < provs.length - 1 ? "1px solid var(--border)" : "none",
                          }}
                        >
                          {/* Provider header */}
                          <div
                            style={{
                              display: "flex",
                              alignItems: "flex-start",
                              justifyContent: "space-between",
                              marginBottom: 10,
                            }}
                          >
                            <div>
                              <div
                                style={{
                                  display: "flex",
                                  alignItems: "center",
                                  gap: 8,
                                  marginBottom: 2,
                                }}
                              >
                                <span style={{ fontSize: 13, fontWeight: 600 }}>
                                  {prov.name}
                                </span>
                                {configured ? (
                                  <CheckCircle
                                    size={13}
                                    strokeWidth={1.75}
                                    style={{ color: "var(--green)" }}
                                  />
                                ) : (
                                  <AlertCircle
                                    size={13}
                                    strokeWidth={1.75}
                                    style={{ color: "var(--text-muted)", opacity: 0.5 }}
                                  />
                                )}
                              </div>
                              <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                                {prov.description}
                              </div>
                            </div>
                            <a
                              href={prov.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: 4,
                                fontSize: 12,
                                color: "var(--accent)",
                                textDecoration: "none",
                                flexShrink: 0,
                              }}
                            >
                              Get key
                              <ExternalLink size={11} strokeWidth={1.75} />
                            </a>
                          </div>

                          {/* Existing key display */}
                          {configured && (
                            <div
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: 8,
                                marginBottom: 8,
                                padding: "6px 10px",
                                background: "var(--bg-elevated)",
                                borderRadius: "var(--radius)",
                                border: "1px solid var(--border)",
                              }}
                            >
                              <CheckCircle
                                size={12}
                                strokeWidth={1.75}
                                style={{ color: "var(--green)", flexShrink: 0 }}
                              />
                              <span
                                style={{
                                  fontSize: 12,
                                  fontFamily: "var(--font-mono)",
                                  color: "var(--text-secondary)",
                                  flex: 1,
                                }}
                              >
                                {maskedValue(prov.id) || "●●●●●●●●●●●●"}
                              </span>
                              <button
                                onClick={() => handleDeleteKey(prov.id)}
                                style={{
                                  background: "none",
                                  border: "none",
                                  cursor: "pointer",
                                  color: "var(--text-muted)",
                                  display: "flex",
                                  padding: 2,
                                }}
                                onMouseEnter={(e) =>
                                  (e.currentTarget.style.color = "var(--red)")
                                }
                                onMouseLeave={(e) =>
                                  (e.currentTarget.style.color = "var(--text-muted)")
                                }
                                title="Remove key"
                              >
                                <Trash2 size={12} strokeWidth={1.75} />
                              </button>
                            </div>
                          )}

                          {/* Input row */}
                          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                            <div style={{ position: "relative", flex: 1 }}>
                              <input
                                className="sentient-input"
                                type={visible ? "text" : "password"}
                                placeholder={
                                  configured
                                    ? "Enter new key to replace…"
                                    : prov.placeholder || "Paste your API key…"
                                }
                                value={draft}
                                onChange={(e) =>
                                  setDraftKeys((p) => ({
                                    ...p,
                                    [prov.id]: e.target.value,
                                  }))
                                }
                                onKeyDown={(e) =>
                                  e.key === "Enter" && handleSaveKey(prov.id)
                                }
                                style={{ paddingRight: 36 }}
                              />
                              <button
                                onClick={() =>
                                  setShowKey((p) => ({ ...p, [prov.id]: !p[prov.id] }))
                                }
                                style={{
                                  position: "absolute",
                                  right: 10,
                                  top: "50%",
                                  transform: "translateY(-50%)",
                                  background: "none",
                                  border: "none",
                                  cursor: "pointer",
                                  color: "var(--text-muted)",
                                  display: "flex",
                                }}
                              >
                                {visible ? (
                                  <EyeOff size={13} strokeWidth={1.75} />
                                ) : (
                                  <Eye size={13} strokeWidth={1.75} />
                                )}
                              </button>
                            </div>
                            <button
                              className="btn btn-primary"
                              onClick={() => handleSaveKey(prov.id)}
                              disabled={!draft.trim() || isSaving}
                              style={{ flexShrink: 0 }}
                            >
                              {isSaving ? "Saving…" : wasSaved ? "Saved ✓" : "Save"}
                            </button>
                          </div>

                          {err && (
                            <div
                              style={{
                                fontSize: 12,
                                color: "var(--red)",
                                marginTop: 6,
                              }}
                            >
                              {err}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* ── SYSTEM CONFIG TAB ────────────────────────────────────────────── */}
      {activeTab === "system" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 16, maxWidth: 560 }}>
          {/* LLM routing */}
          <div className="surface" style={{ padding: "20px 22px" }}>
            <div
              style={{
                fontSize: 13,
                fontWeight: 600,
                marginBottom: 4,
              }}
            >
              LLM routing
            </div>
            <div
              style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 16 }}
            >
              Which model backend agents use by default
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
                  Default backend
                </span>
                <select
                  className="sentient-input"
                  value={sysForm.default_llm ?? "gemini"}
                  onChange={(e) =>
                    setSysForm((p) => ({ ...p, default_llm: e.target.value }))
                  }
                >
                  {LLM_OPTIONS.map((l) => (
                    <option key={l} value={l}>{l}</option>
                  ))}
                </select>
              </label>

              <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
                  Fallback backend
                </span>
                <select
                  className="sentient-input"
                  value={sysForm.fallback_llm ?? "openai"}
                  onChange={(e) =>
                    setSysForm((p) => ({ ...p, fallback_llm: e.target.value }))
                  }
                >
                  {LLM_OPTIONS.map((l) => (
                    <option key={l} value={l}>{l}</option>
                  ))}
                </select>
              </label>
            </div>
          </div>

          {/* Agent runtime */}
          <div className="surface" style={{ padding: "20px 22px" }}>
            <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 4 }}>
              Agent runtime
            </div>
            <div
              style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 16 }}
            >
              Controls how the simulation and agent pool behave
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              <SliderField
                label="Agent tick interval"
                unit="s"
                min={1}
                max={10}
                value={sysForm.agent_tick_interval ?? 2}
                onChange={(v) =>
                  setSysForm((p) => ({ ...p, agent_tick_interval: v }))
                }
                hint="How often agents update their state"
              />
              <SliderField
                label="Max concurrent agents"
                unit=""
                min={5}
                max={100}
                value={sysForm.max_agents ?? 50}
                onChange={(v) =>
                  setSysForm((p) => ({ ...p, max_agents: v }))
                }
                hint="Hard cap on spawnable agent count"
              />
              <SliderField
                label="Memory retention"
                unit=" days"
                min={1}
                max={90}
                value={sysForm.memory_retention_days ?? 30}
                onChange={(v) =>
                  setSysForm((p) => ({ ...p, memory_retention_days: v }))
                }
                hint="How long vector memory entries are kept"
              />
            </div>
          </div>

          {/* Save button */}
          <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
            <button
              className="btn btn-primary"
              onClick={handleSaveSystem}
              disabled={sysSaving}
              style={{ display: "flex", alignItems: "center", gap: 6 }}
            >
              <Save size={13} strokeWidth={1.75} />
              {sysSaving ? "Saving…" : "Save configuration"}
            </button>
            {sysSaved && (
              <span
                style={{
                  fontSize: 13,
                  color: "var(--green)",
                  display: "flex",
                  alignItems: "center",
                  gap: 5,
                }}
              >
                <CheckCircle size={13} strokeWidth={1.75} />
                Saved
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

/* ── Slider field ──────────────────────────────────────────────────────────── */
function SliderField({
  label,
  unit,
  min,
  max,
  value,
  onChange,
  hint,
}: {
  label: string;
  unit: string;
  min: number;
  max: number;
  value: number;
  onChange: (v: number) => void;
  hint: string;
}) {
  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "baseline",
          marginBottom: 6,
        }}
      >
        <label style={{ fontSize: 13, fontWeight: 500 }}>{label}</label>
        <span
          style={{
            fontSize: 13,
            fontFamily: "var(--font-mono)",
            color: "var(--accent)",
            fontWeight: 600,
          }}
        >
          {value}{unit}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        style={{
          width: "100%",
          accentColor: "var(--accent)",
          cursor: "pointer",
        }}
      />
      <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
        {hint}
      </div>
    </div>
  );
}
