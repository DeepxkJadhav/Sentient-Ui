/**
 * Zustand stores for global state management
 */
import { create } from "zustand";
import type { Agent, Goal, MemoryEntry, FederationNode, Plugin, TelemetryMetrics, EventEntry, SwarmTopology, SystemOverview } from "@/lib/api";

// ─── Agent Store ──────────────────────────────────────────────────────────────
interface AgentState {
  agents: Agent[];
  selectedAgent: Agent | null;
  setAgents: (agents: Agent[]) => void;
  updateAgent: (id: string, data: Partial<Agent>) => void;
  setSelectedAgent: (agent: Agent | null) => void;
}

export const useAgentStore = create<AgentState>((set) => ({
  agents: [],
  selectedAgent: null,
  setAgents: (agents) => set({ agents }),
  updateAgent: (id, data) =>
    set((state) => ({
      agents: state.agents.map((a) => (a.id === id ? { ...a, ...data } : a)),
    })),
  setSelectedAgent: (agent) => set({ selectedAgent: agent }),
}));

// ─── Goal Store ───────────────────────────────────────────────────────────────
interface GoalState {
  goals: Goal[];
  setGoals: (goals: Goal[]) => void;
  addGoal: (goal: Goal) => void;
  updateGoal: (id: string, data: Partial<Goal>) => void;
  removeGoal: (id: string) => void;
}

export const useGoalStore = create<GoalState>((set) => ({
  goals: [],
  setGoals: (goals) => set({ goals }),
  addGoal: (goal) => set((state) => ({ goals: [goal, ...state.goals] })),
  updateGoal: (id, data) =>
    set((state) => ({
      goals: state.goals.map((g) => (g.id === id ? { ...g, ...data } : g)),
    })),
  removeGoal: (id) => set((state) => ({ goals: state.goals.filter((g) => g.id !== id) })),
}));

// ─── Memory Store ─────────────────────────────────────────────────────────────
interface MemoryState {
  entries: MemoryEntry[];
  setEntries: (entries: MemoryEntry[]) => void;
  addEntry: (entry: MemoryEntry) => void;
}

export const useMemoryStore = create<MemoryState>((set) => ({
  entries: [],
  setEntries: (entries) => set({ entries }),
  addEntry: (entry) => set((state) => ({ entries: [entry, ...state.entries] })),
}));

// ─── Swarm Store ──────────────────────────────────────────────────────────────
interface SwarmState {
  topology: SwarmTopology | null;
  setTopology: (topology: SwarmTopology) => void;
}

export const useSwarmStore = create<SwarmState>((set) => ({
  topology: null,
  setTopology: (topology) => set({ topology }),
}));

// ─── System Store ─────────────────────────────────────────────────────────────
interface SystemState {
  overview: SystemOverview | null;
  telemetry: TelemetryMetrics | null;
  events: EventEntry[];
  wsConnected: boolean;
  backendOnline: boolean;
  setOverview: (overview: SystemOverview) => void;
  setTelemetry: (telemetry: TelemetryMetrics) => void;
  addEvents: (events: EventEntry[]) => void;
  setWsConnected: (connected: boolean) => void;
  setBackendOnline: (online: boolean) => void;
}

export const useSystemStore = create<SystemState>((set) => ({
  overview: null,
  telemetry: null,
  events: [],
  wsConnected: false,
  backendOnline: false,
  setOverview: (overview) => set({ overview }),
  setTelemetry: (telemetry) => set({ telemetry }),
  addEvents: (events) =>
    set((state) => ({
      events: [...events, ...state.events].slice(0, 200),
    })),
  setWsConnected: (wsConnected) => set({ wsConnected }),
  setBackendOnline: (backendOnline) => set({ backendOnline }),
}));

// ─── Plugin Store ─────────────────────────────────────────────────────────────
interface PluginState {
  plugins: Plugin[];
  setPlugins: (plugins: Plugin[]) => void;
  togglePlugin: (id: string) => void;
}

export const usePluginStore = create<PluginState>((set) => ({
  plugins: [],
  setPlugins: (plugins) => set({ plugins }),
  togglePlugin: (id) =>
    set((state) => ({
      plugins: state.plugins.map((p) => (p.id === id ? { ...p, enabled: !p.enabled } : p)),
    })),
}));

// ─── Federation Store ─────────────────────────────────────────────────────────
interface FederationState {
  nodes: FederationNode[];
  setNodes: (nodes: FederationNode[]) => void;
}

export const useFederationStore = create<FederationState>((set) => ({
  nodes: [],
  setNodes: (nodes) => set({ nodes }),
}));
