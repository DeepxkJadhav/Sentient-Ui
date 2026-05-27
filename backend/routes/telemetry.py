"""Telemetry routes — system metrics and LLM routing stats"""
import random
import time
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from database import get_db
from models import Agent, Event

router = APIRouter()


@router.get("/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db)):
    agents = (await db.execute(select(Agent))).scalars().all()
    active = [a for a in agents if a.status in ("thinking", "executing")]
    return {
        "cpu_percent": round(sum(a.cpu_percent for a in agents) / max(len(agents), 1), 1),
        "memory_percent": round(random.uniform(35, 72), 1),
        "gpu_percent": round(random.uniform(20, 85) if active else random.uniform(5, 20), 1),
        "network_mbps": round(random.uniform(15, 220), 1),
        "disk_read_mbps": round(random.uniform(5, 80), 1),
        "disk_write_mbps": round(random.uniform(2, 40), 1),
        "active_agents": len(active),
        "total_agents": len(agents),
        "tokens_per_sec": round(len(active) * random.uniform(50, 200), 0),
        "requests_per_sec": round(len(active) * random.uniform(0.5, 4.0), 1),
        "latency_p50": round(random.uniform(80, 200), 1),
        "latency_p95": round(random.uniform(300, 900), 1),
        "latency_p99": round(random.uniform(600, 1500), 1),
        "total_tokens_used": sum(a.tokens_used for a in agents),
        "total_tasks_completed": sum(a.tasks_completed for a in agents),
        "timestamp": time.time(),
    }


@router.get("/llm-router")
async def llm_router_stats(db: AsyncSession = Depends(get_db)):
    agents = (await db.execute(select(Agent))).scalars().all()
    dist = {}
    for a in agents:
        dist[a.llm_backend] = dist.get(a.llm_backend, 0) + 1
    return {
        "distribution": dist,
        "agents_per_backend": [
            {"backend": k, "count": v, "tokens": random.randint(10000, 500000)}
            for k, v in dist.items()
        ],
        "routing_policy": "round-robin-with-failover",
    }


@router.get("/events")
async def get_events(limit: int = Query(50, le=200), db: AsyncSession = Depends(get_db)):
    events = (await db.execute(select(Event).order_by(desc(Event.created_at)).limit(limit))).scalars().all()
    return [{"id": e.id, "type": e.type, "source": e.source, "message": e.message, "severity": e.severity, "ts": e.created_at.isoformat()} for e in events]


@router.get("/history")
async def telemetry_history():
    """Generate historical telemetry data for charts"""
    now = time.time()
    data = []
    for i in range(60):
        ts = now - (59 - i) * 2
        data.append({
            "timestamp": ts,
            "cpu": round(random.uniform(20, 75), 1),
            "memory": round(random.uniform(30, 70), 1),
            "gpu": round(random.uniform(15, 90), 1),
            "network": round(random.uniform(10, 200), 1),
            "tokens_per_sec": round(random.uniform(100, 800), 0),
        })
    return data
