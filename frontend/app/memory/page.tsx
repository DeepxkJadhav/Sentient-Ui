"use client";
import { useEffect, useState } from "react";
import { Brain, Search, Plus, Trash2, X } from "lucide-react";
import { memoryApi, type MemoryEntry, type MemoryStats } from "@/lib/api";

export default function MemoryPage() {
  const [entries, setEntries] = useState<MemoryEntry[]>([]);
  const [stats, setStats] = useState<MemoryStats | null>(null);
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState<{ memory: MemoryEntry; similarity: number }[] | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [newContent, setNewContent] = useState("");
  const [adding, setAdding] = useState(false);

  const load = () => {
    memoryApi.list({ limit: 100, category: selectedCategory || undefined }).then(setEntries).catch(() => {});
    memoryApi.stats().then(setStats).catch(() => {});
  };

  useEffect(() => { load(); }, [selectedCategory]);

  const handleSearch = async () => {
    if (!query.trim()) { setSearchResults(null); return; }
    setLoading(true);
    try {
      const results = await memoryApi.search(query, 10);
      setSearchResults(results);
    } finally {
      setLoading(false);
    }
  };

  const handleAddMemory = async () => {
    if (!newContent.trim()) return;
    await memoryApi.create({ content: newContent, category: "general" });
    setNewContent("");
    setAdding(false);
    load();
  };

  const handleDelete = async (id: string) => {
    await memoryApi.delete(id);
    setEntries((prev) => prev.filter((e) => e.id !== id));
    if (searchResults) setSearchResults((prev) => prev?.filter((r) => r.memory.id !== id) || null);
  };

  const displayEntries = searchResults ? searchResults.map((r) => r.memory) : entries;

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 24 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
            <Brain size={16} strokeWidth={1.75} style={{ color: "var(--text-muted)" }} />
            <h1 style={{ fontSize: 18, fontWeight: 600 }}>Memory</h1>
          </div>
          <p style={{ fontSize: 13, color: "var(--text-secondary)" }}>
            {stats?.total ?? 0} entries · {stats?.vector_dimensions ?? 128}d embeddings
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => setAdding(true)}>
          <Plus size={13} strokeWidth={1.75} />
          Add entry
        </button>
      </div>

      {/* Search */}
      <div style={{ display: "flex", gap: 8, marginBottom: 14 }}>
        <div style={{ position: "relative", flex: 1 }}>
          <Search
            size={13}
            strokeWidth={1.75}
            style={{
              position: "absolute",
              left: 11,
              top: "50%",
              transform: "translateY(-50%)",
              color: "var(--text-muted)",
            }}
          />
          <input
            className="sentient-input"
            style={{ paddingLeft: 32 }}
            placeholder="Semantic search across memory…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
        </div>
        <button className="btn btn-primary" onClick={handleSearch} disabled={loading}>
          {loading ? "…" : "Search"}
        </button>
        {searchResults && (
          <button className="btn btn-ghost" onClick={() => setSearchResults(null)}>
            <X size={13} strokeWidth={1.75} />
            Clear
          </button>
        )}
      </div>

      {/* Category filter */}
      {stats && (
        <div style={{ display: "flex", gap: 6, marginBottom: 16, flexWrap: "wrap" }}>
          <button
            className={`badge ${!selectedCategory ? "badge-accent" : "badge-muted"}`}
            style={{ cursor: "pointer", border: "none", fontFamily: "var(--font-sans)" }}
            onClick={() => setSelectedCategory(null)}
          >
            All ({stats.total})
          </button>
          {Object.entries(stats.categories).map(([cat, count]) => (
            <button
              key={cat}
              className={`badge ${selectedCategory === cat ? "badge-accent" : "badge-muted"}`}
              style={{ cursor: "pointer", border: "none", fontFamily: "var(--font-sans)", textTransform: "none" }}
              onClick={() => setSelectedCategory(cat === selectedCategory ? null : cat)}
            >
              {cat} ({count})
            </button>
          ))}
        </div>
      )}

      {/* Entry grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 10 }}>
        {displayEntries.map((entry) => {
          const similarity = searchResults?.find((r) => r.memory.id === entry.id)?.similarity;
          return (
            <div
              key={entry.id}
              className="card"
              style={{ padding: "14px 16px" }}
              onMouseEnter={(e) => {
                (e.currentTarget.querySelector(".delete-btn") as HTMLElement)?.style.setProperty("opacity", "1");
              }}
              onMouseLeave={(e) => {
                (e.currentTarget.querySelector(".delete-btn") as HTMLElement)?.style.setProperty("opacity", "0");
              }}
            >
              {/* Top row */}
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <span className="badge badge-muted" style={{ textTransform: "none" }}>
                    {entry.category}
                  </span>
                  {similarity !== undefined && (
                    <span className="badge badge-green">
                      {(similarity * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
                <button
                  className="delete-btn"
                  style={{
                    opacity: 0,
                    transition: "opacity 0.14s ease",
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    color: "var(--text-muted)",
                    display: "flex",
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.color = "var(--red)")}
                  onMouseLeave={(e) => (e.currentTarget.style.color = "var(--text-muted)")}
                  onClick={() => handleDelete(entry.id)}
                >
                  <Trash2 size={12} strokeWidth={1.75} />
                </button>
              </div>

              {/* Content */}
              <p
                style={{
                  fontSize: 13,
                  color: "var(--text-secondary)",
                  marginBottom: 10,
                  display: "-webkit-box",
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: "vertical",
                  overflow: "hidden",
                }}
              >
                {entry.content}
              </p>

              {/* Footer */}
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                  {entry.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      style={{
                        fontSize: 11,
                        fontFamily: "var(--font-mono)",
                        color: "var(--text-muted)",
                        background: "var(--bg-hover)",
                        padding: "1px 6px",
                        borderRadius: "var(--radius-sm)",
                      }}
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
                <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                  {new Date(entry.created_at).toLocaleDateString()}
                </span>
              </div>

              {/* Importance bar */}
              <div className="progress-bar" style={{ marginTop: 10 }}>
                <div
                  className="progress-fill"
                  style={{ width: `${entry.importance * 100}%`, background: "var(--accent)" }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {displayEntries.length === 0 && (
        <div style={{ textAlign: "center", padding: "56px 0", color: "var(--text-muted)", fontSize: 13 }}>
          {loading ? "Searching…" : "No entries found"}
        </div>
      )}

      {/* Add modal */}
      {adding && (
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
          onClick={() => setAdding(false)}
        >
          <div
            style={{
              background: "var(--bg-elevated)",
              border: "1px solid var(--border-mid)",
              borderRadius: "var(--radius-lg)",
              padding: 24,
              width: 400,
              display: "flex",
              flexDirection: "column",
              gap: 14,
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ fontSize: 15, fontWeight: 600 }}>Add memory entry</div>
            <textarea
              className="sentient-input"
              style={{ height: 120, resize: "none" }}
              placeholder="Enter content to store in the shared vector store…"
              value={newContent}
              onChange={(e) => setNewContent(e.target.value)}
            />
            <div style={{ display: "flex", gap: 8 }}>
              <button className="btn btn-ghost" style={{ flex: 1 }} onClick={() => setAdding(false)}>
                Cancel
              </button>
              <button className="btn btn-primary" style={{ flex: 1 }} onClick={handleAddMemory}>
                Store
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
