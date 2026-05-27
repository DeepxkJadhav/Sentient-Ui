"""
Agent Simulator — Auto-cycles agents through realistic lifecycle states
and broadcasts WebSocket events to all connected clients.

When an agent transitions to 'thinking' or 'executing', the simulator
calls the real LLM API configured in settings.json (if a key exists).
Falls back to simulated tasks transparently if no key is available.
"""
import asyncio
import random
import time
from datetime import datetime
from typing import TYPE_CHECKING

from database import AsyncSessionLocal
from models import Agent, Event, MemoryEntry, SwarmEdge
from sqlalchemy import select
from constants import AGENT_TASKS
from services.llm_service import get_agent_task

if TYPE_CHECKING:
    from main import ConnectionManager

# Per-agent cooldown: don't call LLM more than once per N seconds
LLM_COOLDOWN = 30.0


class AgentSimulator:
    def __init__(self, manager: "ConnectionManager"):
        self.manager = manager
        self.running = True
        self.tick = 0
        self.telemetry_history: list[dict] = []
        # agent_id → timestamp of last LLM call
        self._llm_last_called: dict[str, float] = {}

    async def run(self):
        """Main simulation loop"""
        while self.running:
            try:
                await self._tick()
                await asyncio.sleep(2.0)
                self.tick += 1
            except Exception as e:
                print(f"Simulator error: {e}", flush=True)
                await asyncio.sleep(5)

    async def _tick(self):
        async with AsyncSessionLocal() as db:
            agents = (await db.execute(select(Agent))).scalars().all()
            if not agents:
                return

            events = []

            # --- Determine next states first (sync) ---
            transitions = {}
            for agent in agents:
                new_status, _ = self._next_state(agent)
                transitions[agent.id] = new_status

            # --- Fire LLM calls for agents entering thinking/executing ---
            llm_tasks = {}
            now = time.time()
            for agent in agents:
                new_status = transitions[agent.id]
                old_status = agent.status
                entering_active = (
                    new_status in ("thinking", "executing")
                    and (old_status != new_status or agent.current_task is None)
                )
                cooldown_ok = (
                    now - self._llm_last_called.get(agent.id, 0) >= LLM_COOLDOWN
                )
                if entering_active and cooldown_ok:
                    llm_tasks[agent.id] = asyncio.create_task(
                        get_agent_task(agent.name, agent.role, agent.llm_backend, new_status)
                    )
                    self._llm_last_called[agent.id] = now

            # Gather LLM results (with timeout so slow APIs don't stall the loop)
            llm_results: dict[str, tuple[str, bool]] = {}
            if llm_tasks:
                done = await asyncio.gather(
                    *llm_tasks.values(), return_exceptions=True
                )
                for agent_id, result in zip(llm_tasks.keys(), done):
                    if isinstance(result, Exception):
                        llm_results[agent_id] = (random.choice(AGENT_TASKS), False)
                    else:
                        llm_results[agent_id] = result  # (text, is_real)

            # --- Apply updates ---
            for agent in agents:
                old_status = agent.status
                new_status = transitions[agent.id]

                agent.status = new_status
                agent.cpu_percent = self._cpu_for_status(new_status)
                agent.memory_mb = round(random.uniform(64, 512), 1)
                agent.latency_ms = round(random.uniform(10, 800), 1)

                # Apply LLM result if we have one for this agent
                if agent.id in llm_results:
                    task_text, is_real = llm_results[agent.id]
                    agent.current_task = task_text
                    agent.last_llm_output = task_text
                    agent.is_llm_real = is_real
                    if is_real:
                        print(
                            f"[LLM ✓] {agent.name} ({agent.llm_backend}): {task_text[:60]}",
                            flush=True,
                        )
                elif new_status == "idle":
                    agent.current_task = None
                elif new_status == "error":
                    agent.current_task = "Encountered unexpected exception in task pipeline"
                    agent.is_llm_real = False
                # If staying in same active state with no new LLM call, keep current_task

                if new_status == "executing":
                    agent.tokens_used += random.randint(50, 500)

                if old_status == "executing" and new_status == "idle":
                    agent.tasks_completed += 1
                    agent.last_active = datetime.utcnow()

                    # Write to shared memory
                    memory = MemoryEntry(
                        agent_id=agent.id,
                        content=agent.last_llm_output or f"Completed task by {agent.name}",
                        summary=f"Agent {agent.name} completed: {agent.current_task or 'task'}",
                        category=self._category_for_role(agent.role),
                        importance=round(random.uniform(0.3, 1.0), 2),
                        tags=[agent.role.lower().replace(" ", "_"), "completed",
                              "llm_real" if agent.is_llm_real else "simulated"],
                    )
                    db.add(memory)

                    events.append({
                        "type": "agent_task_complete",
                        "source": agent.name,
                        "message": f"{agent.name} completed: {agent.current_task or 'task'}",
                        "severity": "success",
                        "agent_id": agent.id,
                    })

                if old_status != new_status:
                    llm_badge = " [real LLM]" if agent.is_llm_real and new_status in ("thinking", "executing") else ""
                    events.append({
                        "type": "agent_status_change",
                        "source": agent.name,
                        "message": f"{agent.name} → {new_status}{llm_badge}",
                        "severity": "info",
                        "agent_id": agent.id,
                    })

            await db.commit()

            # Persist events
            for ev_data in events[:3]:
                event = Event(
                    type=ev_data["type"],
                    source=ev_data["source"],
                    message=ev_data["message"],
                    severity=ev_data["severity"],
                    agent_id=ev_data.get("agent_id"),
                )
                db.add(event)
            if events:
                await db.commit()

            # Broadcast
            agent_payloads = [self._agent_dict(a) for a in agents]
            telemetry = self._generate_telemetry(agents)
            self.telemetry_history.append(telemetry)
            if len(self.telemetry_history) > 60:
                self.telemetry_history.pop(0)

            await self.manager.broadcast({
                "type": "agents_update",
                "data": agent_payloads,
                "timestamp": time.time(),
            })
            await self.manager.broadcast({
                "type": "telemetry_update",
                "data": telemetry,
                "timestamp": time.time(),
            })
            if events:
                await self.manager.broadcast({
                    "type": "events",
                    "data": events[:5],
                    "timestamp": time.time(),
                })

            if self.tick % 5 == 0:
                swarm_data = self._generate_swarm_topology(agents)
                await self.manager.broadcast({
                    "type": "swarm_update",
                    "data": swarm_data,
                    "timestamp": time.time(),
                })

    def _next_state(self, agent: Agent) -> tuple[str, str | None]:
        transitions = {
            "idle":      [("thinking", 0.35), ("idle", 0.65)],
            "thinking":  [("executing", 0.7), ("idle", 0.2), ("error", 0.1)],
            "executing": [("idle", 0.4), ("executing", 0.55), ("error", 0.05)],
            "error":     [("idle", 0.8), ("error", 0.2)],
            "offline":   [("idle", 0.1), ("offline", 0.9)],
        }
        choices = transitions.get(agent.status, [("idle", 1.0)])
        statuses, weights = zip(*choices)
        new_status = random.choices(statuses, weights=weights)[0]
        task = agent.current_task
        if new_status == "idle":
            task = None
        elif new_status == "error":
            task = "Encountered unexpected exception in task pipeline"
        return new_status, task

    def _cpu_for_status(self, status: str) -> float:
        mapping = {
            "idle":      round(random.uniform(0.5, 3.0), 1),
            "thinking":  round(random.uniform(15, 40), 1),
            "executing": round(random.uniform(40, 90), 1),
            "error":     round(random.uniform(5, 20), 1),
            "offline":   0.0,
        }
        return mapping.get(status, 0.0)

    def _category_for_role(self, role: str) -> str:
        mapping = {
            "Code Architect":    "architecture",
            "Backend Engineer":  "backend",
            "Frontend Engineer": "frontend",
            "Security Auditor":  "security",
            "DevOps Agent":      "devops",
            "ML Engineer":       "ml",
            "Testing Agent":     "testing",
            "Planner Agent":     "planning",
            "Research Agent":    "research",
            "Documentation Agent": "docs",
            "Debugging Agent":   "debugging",
            "Database Optimizer": "database",
        }
        return mapping.get(role, "general")

    def _agent_dict(self, agent: Agent) -> dict:
        return {
            "id":              agent.id,
            "name":            agent.name,
            "role":            agent.role,
            "status":          agent.status,
            "llm_backend":     agent.llm_backend,
            "current_task":    agent.current_task,
            "last_llm_output": agent.last_llm_output,
            "is_llm_real":     agent.is_llm_real,
            "cpu_percent":     agent.cpu_percent,
            "memory_mb":       agent.memory_mb,
            "tokens_used":     agent.tokens_used,
            "tasks_completed": agent.tasks_completed,
            "latency_ms":      agent.latency_ms,
            "color":           agent.color,
            "icon":            agent.icon,
        }

    def _generate_telemetry(self, agents: list) -> dict:
        active = [a for a in agents if a.status in ("thinking", "executing")]
        real_count = sum(1 for a in agents if a.is_llm_real)
        return {
            "cpu_percent":        round(sum(a.cpu_percent for a in agents) / max(len(agents), 1), 1),
            "memory_percent":     round(random.uniform(30, 75), 1),
            "gpu_percent":        round(random.uniform(20, 85) if active else random.uniform(5, 20), 1),
            "network_mbps":       round(random.uniform(10, 200), 1),
            "disk_read_mbps":     round(random.uniform(1, 50), 1),
            "disk_write_mbps":    round(random.uniform(1, 30), 1),
            "active_agents":      len(active),
            "total_agents":       len(agents),
            "real_llm_agents":    real_count,
            "tokens_per_sec":     round(sum(a.tokens_used for a in active) / max(len(active), 1) / 100, 1),
            "requests_per_sec":   round(len(active) * random.uniform(0.5, 3.0), 1),
            "latency_p50":        round(random.uniform(80, 200), 1),
            "latency_p95":        round(random.uniform(300, 800), 1),
            "latency_p99":        round(random.uniform(600, 1200), 1),
            "total_tokens_used":  sum(a.tokens_used for a in agents),
            "total_tasks_completed": sum(a.tasks_completed for a in agents),
            "timestamp":          time.time(),
            "llm_distribution": {
                "openai": len([a for a in agents if a.llm_backend == "openai"]),
                "claude": len([a for a in agents if a.llm_backend == "claude"]),
                "gemini": len([a for a in agents if a.llm_backend == "gemini"]),
                "ollama": len([a for a in agents if a.llm_backend == "ollama"]),
            },
        }

    def _generate_swarm_topology(self, agents: list) -> dict:
        nodes = []
        edges = []
        active = [a for a in agents if a.status in ("thinking", "executing")]

        for agent in agents:
            nodes.append({
                "id":         agent.id,
                "name":       agent.name,
                "role":       agent.role,
                "status":     agent.status,
                "color":      agent.color,
                "icon":       agent.icon,
                "cpu":        agent.cpu_percent,
                "is_llm_real": agent.is_llm_real,
            })

        for i, a1 in enumerate(active):
            for a2 in active[i + 1:]:
                if random.random() < 0.4:
                    edges.append({
                        "source":   a1.id,
                        "target":   a2.id,
                        "strength": round(random.uniform(0.3, 1.0), 2),
                        "messages": random.randint(1, 50),
                    })

        return {"nodes": nodes, "edges": edges, "mode": "hybrid-mesh"}
