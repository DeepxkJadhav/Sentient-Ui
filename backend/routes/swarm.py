"""Swarm, Federation, Plugins, Telemetry routes"""
# swarm.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import random
from database import get_db
from models import Agent

router = APIRouter()


@router.get("/topology")
async def get_topology(db: AsyncSession = Depends(get_db)):
    agents = (await db.execute(select(Agent))).scalars().all()
    nodes = [{"id": a.id, "name": a.name, "role": a.role, "status": a.status, "color": a.color, "icon": a.icon, "cpu": a.cpu_percent} for a in agents]
    active = [a for a in agents if a.status in ("thinking", "executing")]
    edges = []
    for i, a1 in enumerate(active):
        for a2 in active[i + 1:]:
            if random.random() < 0.5:
                edges.append({"source": a1.id, "target": a2.id, "strength": round(random.uniform(0.3, 1.0), 2), "messages": random.randint(1, 100)})
    return {"nodes": nodes, "edges": edges, "mode": "hybrid-mesh"}


@router.get("/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db)):
    agents = (await db.execute(select(Agent))).scalars().all()
    active = [a for a in agents if a.status in ("thinking", "executing")]
    return {
        "total_agents": len(agents),
        "active_agents": len(active),
        "messages_per_sec": round(len(active) * random.uniform(10, 40), 1),
        "total_channels": len(active) * (len(active) - 1) // 2 if len(active) > 1 else 0,
        "avg_latency_ms": round(random.uniform(15, 80), 1),
        "coordinator": "Oracle (Planner)",
        "topology_mode": "hybrid-mesh",
    }
