"""
Sentient-UI Backend — FastAPI Multi-Agent Orchestration API
"""
import asyncio
import json
import random
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import init_db, get_db, AsyncSessionLocal
from models import Agent, Goal, MemoryEntry, FederationNode, Plugin, Event

from simulation.agent_simulator import AgentSimulator
from routes import agents, goals, memory, swarm, federation, plugins, telemetry, settings


def log(msg): print(msg, flush=True)

# ─── WebSocket Connection Manager ─────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS] Connected. Total: {len(self.active_connections)}", flush=True)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"[WS] Disconnected. Total: {len(self.active_connections)}", flush=True)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()
simulator: Optional[AgentSimulator] = None

# ─── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    global simulator
    log("[Sentient-UI] Backend starting...")
    await init_db()
    log("[Sentient-UI] Database initialized")

    simulator = AgentSimulator(manager)
    asyncio.create_task(simulator.run())
    log("[Sentient-UI] Agent simulator started")
    log("[Sentient-UI] Backend ready on http://localhost:8000")

    yield

    log("[Sentient-UI] Backend shutting down...")
    if simulator:
        simulator.running = False

# ─── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Sentient-UI API",
    description="Multi-Agent Orchestration Platform Backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Desktop app + any local frontend
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────

app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(goals.router, prefix="/api/goals", tags=["Goals"])
app.include_router(memory.router, prefix="/api/memory", tags=["Memory"])
app.include_router(swarm.router, prefix="/api/swarm", tags=["Swarm"])
app.include_router(federation.router, prefix="/api/federation", tags=["Federation"])
app.include_router(plugins.router, prefix="/api/plugins", tags=["Plugins"])
app.include_router(telemetry.router, prefix="/api/telemetry", tags=["Telemetry"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])

# ─── WebSocket ────────────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, server pushes data
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong", "timestamp": time.time()})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"[WS] Error: {e}", flush=True)
        manager.disconnect(websocket)

# ─── Health ───────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {
        "status": "online",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "ws_connections": len(manager.active_connections),
    }

@app.get("/api/system/overview")
async def system_overview():
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select, func
        from models import Agent, Goal, MemoryEntry, Event

        agent_count = await db.execute(select(func.count(Agent.id)))
        goal_count = await db.execute(select(func.count(Goal.id)))
        memory_count = await db.execute(select(func.count(MemoryEntry.id)))
        event_count = await db.execute(select(func.count(Event.id)))

        return {
            "agents": {"total": agent_count.scalar()},
            "goals": {"total": goal_count.scalar()},
            "memory": {"total": memory_count.scalar()},
            "events": {"total": event_count.scalar()},
            "swarm": {
                "active_channels": random.randint(8, 24),
                "messages_per_sec": round(random.uniform(120, 340), 1),
                "topology": "hybrid-mesh",
            },
            "system": {
                "uptime_seconds": int(time.time() % 86400),
                "cpu_percent": round(random.uniform(20, 65), 1),
                "memory_percent": round(random.uniform(30, 70), 1),
                "gpu_percent": round(random.uniform(10, 85), 1),
            },
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
