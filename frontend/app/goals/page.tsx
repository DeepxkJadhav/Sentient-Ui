"use client";
import { useEffect, useState, useRef } from "react";
import { Target, Plus, Trash2, Loader } from "lucide-react";
import { goalsApi, type Goal, type GoalDetail } from "@/lib/api";

const STATUS_LABEL: Record<string, string> = {
  pending:     "Pending",
  decomposing: "Decomposing",
  running:     "Running",
  completed:   "Completed",
  failed:      "Failed",
};

const STATUS_COLOR: Record<string, string> = {
  pending:     "var(--text-muted)",
  decomposing: "var(--blue)",
  running:     "var(--accent)",
  completed:   "var(--green)",
  failed:      "var(--red)",
};

export default function GoalsPage() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [selected, setSelected] = useState<GoalDetail | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState(5);
  const [loading, setLoading] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const load = () => goalsApi.list().then(setGoals).catch(() => {});

  useEffect(() => {
    load();
    pollRef.current = setInterval(load, 4000);
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, []);

  useEffect(() => {
    if (!selected) return;
    const refresh = () => goalsApi.get(selected.id).then(setSelected).catch(() => {});
    refresh();
    const iv = setInterval(refresh, 3000);
    return () => clearInterval(iv);
  }, [selected?.id]);

  const handleCreate = async () => {
    if (!title.trim()) return;
    setLoading(true);
    try {
      const goal = await goalsApi.create({ title, description, priority });
      setGoals((prev) => [goal, ...prev]);
      setTitle("");
      setDescription("");
      goalsApi.get(goal.id).then(setSelected).catch(() => {});
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    await goalsApi.delete(id);
    setGoals((prev) => prev.filter((g) => g.id !== id));
    if (selected?.id === id) setSelected(null);
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
          <Target size={16} strokeWidth={1.75} style={{ color: "var(--text-muted)" }} />
          <h1 style={{ fontSize: 18, fontWeight: 600 }}>Goals</h1>
        </div>
        <p style={{ fontSize: 13, color: "var(--text-secondary)" }}>
          Autonomous task decomposition via DAG planner
        </p>
      </div>

      {/* Goal input form */}
      <div className="surface" style={{ padding: "16px 20px", marginBottom: 20 }}>
        <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 12 }}>
          New goal — decomposed automatically into subtasks
        </div>
        <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
          <input
            className="sentient-input"
            style={{ flex: 1 }}
            placeholder="Describe a high-level goal…"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleCreate()}
          />
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
            <label style={{ fontSize: 12, color: "var(--text-muted)" }}>Priority</label>
            <select
              className="sentient-input"
              style={{ width: 64 }}
              value={priority}
              onChange={(e) => setPriority(Number(e.target.value))}
            >
              {[1,2,3,4,5,6,7,8,9,10].map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
        </div>
        <textarea
          className="sentient-input"
          style={{ height: 60, resize: "none", marginBottom: 10 }}
          placeholder="Optional context or constraints…"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <button
          className="btn btn-primary"
          onClick={handleCreate}
          disabled={loading || !title.trim()}
        >
          {loading ? (
            <>
              <Loader size={12} strokeWidth={1.75} style={{ animation: "spin 1s linear infinite" }} />
              Decomposing…
            </>
          ) : (
            <>Submit</>
          )}
        </button>
      </div>

      {/* Two-column */}
      <div style={{ display: "grid", gridTemplateColumns: "2fr 3fr", gap: 12 }}>
        {/* Goals queue */}
        <div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 10 }}>
            Queue ({goals.length})
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {goals.map((goal) => {
              const isActive = selected?.id === goal.id;
              return (
                <div
                  key={goal.id}
                  className={`card ${isActive ? "selected" : ""}`}
                  style={{ padding: "12px 14px", cursor: "pointer" }}
                  onClick={() =>
                    isActive
                      ? setSelected(null)
                      : goalsApi.get(goal.id).then(setSelected).catch(() => {})
                  }
                >
                  <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 8 }}>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 13, fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {goal.title}
                      </div>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 4 }}>
                        <span
                          style={{
                            fontSize: 11,
                            color: STATUS_COLOR[goal.status] || "var(--text-muted)",
                          }}
                        >
                          {STATUS_LABEL[goal.status] || goal.status}
                        </span>
                        <span style={{ fontSize: 11, color: "var(--text-muted)" }}>
                          P{goal.priority}
                        </span>
                      </div>
                    </div>
                    <button
                      style={{
                        background: "none",
                        border: "none",
                        cursor: "pointer",
                        color: "var(--text-muted)",
                        display: "flex",
                        flexShrink: 0,
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.color = "var(--red)")}
                      onMouseLeave={(e) => (e.currentTarget.style.color = "var(--text-muted)")}
                      onClick={(e) => handleDelete(goal.id, e)}
                    >
                      <Trash2 size={12} strokeWidth={1.75} />
                    </button>
                  </div>
                  {goal.status !== "pending" && (
                    <div style={{ marginTop: 8 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "var(--text-muted)", marginBottom: 4 }}>
                        <span>Progress</span>
                        <span>{goal.progress}%</span>
                      </div>
                      <div className="progress-bar">
                        <div
                          className="progress-fill"
                          style={{
                            width: `${goal.progress}%`,
                            background: STATUS_COLOR[goal.status] || "var(--accent)",
                          }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
            {goals.length === 0 && (
              <div style={{ padding: "40px 0", textAlign: "center", color: "var(--text-muted)", fontSize: 13 }}>
                No goals yet
              </div>
            )}
          </div>
        </div>

        {/* DAG / task list */}
        <div>
          {selected ? (
            <DAGView goal={selected} />
          ) : (
            <div
              className="surface"
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                padding: 40,
                textAlign: "center",
                color: "var(--text-muted)",
                gap: 8,
              }}
            >
              <Target size={24} strokeWidth={1.25} />
              <span style={{ fontSize: 13 }}>Select a goal to view its task breakdown</span>
            </div>
          )}
        </div>
      </div>

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

function DAGView({ goal }: { goal: GoalDetail }) {
  const tasks = goal.tasks || [];
  const color = STATUS_COLOR[goal.status] || "var(--accent)";

  return (
    <div className="surface" style={{ padding: "16px 20px", height: "100%", overflowY: "auto" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
        <div>
          <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 2 }}>{goal.title}</div>
          <div style={{ fontSize: 12, color }}>
            {STATUS_LABEL[goal.status] || goal.status} · {goal.progress}%
          </div>
        </div>
        <span className="badge badge-muted">{tasks.length} tasks</span>
      </div>

      {goal.status === "decomposing" && (
        <div style={{ textAlign: "center", padding: "32px 0" }}>
          <Loader
            size={24}
            strokeWidth={1.75}
            style={{
              margin: "0 auto 10px",
              color: "var(--blue)",
              display: "block",
              animation: "spin 1s linear infinite",
            }}
          />
          <div style={{ fontSize: 13, color: "var(--text-secondary)" }}>
            Decomposing into subtasks…
          </div>
        </div>
      )}

      {tasks.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {tasks.map((task, i) => {
            const done = task.status === "completed";
            return (
              <div
                key={task.id}
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  gap: 12,
                  padding: "10px 12px",
                  borderRadius: "var(--radius)",
                  background: "var(--bg-elevated)",
                }}
              >
                {/* Step circle */}
                <div
                  style={{
                    width: 22,
                    height: 22,
                    borderRadius: "50%",
                    border: `1px solid ${done ? "var(--green)" : "var(--border-mid)"}`,
                    background: done ? "rgba(52,211,153,0.1)" : "transparent",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 10,
                    fontFamily: "var(--font-mono)",
                    color: done ? "var(--green)" : "var(--text-muted)",
                    flexShrink: 0,
                  }}
                >
                  {done ? "✓" : i + 1}
                </div>

                {/* Task info */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 13, color: done ? "var(--text-muted)" : "var(--text-primary)" }}>
                    {task.title}
                  </div>
                  {task.depends_on && task.depends_on.length > 0 && (
                    <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
                      Depends on {task.depends_on.length} task{task.depends_on.length > 1 ? "s" : ""}
                    </div>
                  )}
                </div>

                {/* Status */}
                <span
                  className={`badge ${done ? "badge-green" : "badge-muted"}`}
                  style={{ flexShrink: 0 }}
                >
                  {task.status}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
