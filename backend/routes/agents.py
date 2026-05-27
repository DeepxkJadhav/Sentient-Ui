"""Agents routes"""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models import Agent

router = APIRouter()


class AgentCreate(BaseModel):
    name: str
    role: str
    llm_backend: str = "gemini"
    color: str = "#FFD700"
    icon: str = "🤖"


class AgentUpdate(BaseModel):
    status: Optional[str] = None
    llm_backend: Optional[str] = None
    current_task: Optional[str] = None


@router.get("/")
async def list_agents(db: AsyncSession = Depends(get_db)):
    agents = (await db.execute(select(Agent))).scalars().all()
    return [_agent_dict(a) for a in agents]


@router.get("/{agent_id}")
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    agent = await db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return _agent_dict(agent)


@router.post("/")
async def create_agent(body: AgentCreate, db: AsyncSession = Depends(get_db)):
    agent = Agent(
        id=str(uuid.uuid4()),
        name=body.name,
        role=body.role,
        llm_backend=body.llm_backend,
        color=body.color,
        icon=body.icon,
        status="idle",
        is_builtin=False,
        created_at=datetime.utcnow(),
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return _agent_dict(agent)


@router.patch("/{agent_id}")
async def update_agent(agent_id: str, body: AgentUpdate, db: AsyncSession = Depends(get_db)):
    agent = await db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if body.status is not None:
        agent.status = body.status
    if body.llm_backend is not None:
        agent.llm_backend = body.llm_backend
    if body.current_task is not None:
        agent.current_task = body.current_task
    await db.commit()
    return _agent_dict(agent)


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    agent = await db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if agent.is_builtin:
        raise HTTPException(status_code=400, detail="Cannot delete built-in agents")
    await db.delete(agent)
    await db.commit()
    return {"deleted": agent_id}


@router.post("/{agent_id}/restart")
async def restart_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    agent = await db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent.status = "idle"
    agent.current_task = None
    agent.cpu_percent = 0.0
    await db.commit()
    return {"status": "restarted", "agent_id": agent_id}


@router.get("/{agent_id}/logs")
async def get_agent_logs(agent_id: str, db: AsyncSession = Depends(get_db)):
    from models import Event
    events = (await db.execute(
        select(Event).where(Event.agent_id == agent_id).order_by(Event.created_at.desc()).limit(50)
    )).scalars().all()
    return [{"id": e.id, "type": e.type, "message": e.message, "severity": e.severity, "ts": e.created_at.isoformat()} for e in events]


def _agent_dict(agent: Agent) -> dict:
    return {
        "id": agent.id,
        "name": agent.name,
        "role": agent.role,
        "status": agent.status,
        "llm_backend": agent.llm_backend,
        "current_task": agent.current_task,
        "cpu_percent": agent.cpu_percent,
        "memory_mb": agent.memory_mb,
        "tokens_used": agent.tokens_used,
        "tasks_completed": agent.tasks_completed,
        "latency_ms": agent.latency_ms,
        "color": agent.color,
        "icon": agent.icon,
        "is_builtin": agent.is_builtin,
        "created_at": agent.created_at.isoformat() if agent.created_at else None,
        "last_active": agent.last_active.isoformat() if agent.last_active else None,
    }
