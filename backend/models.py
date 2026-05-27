"""
SQLAlchemy ORM Models
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


def gen_id():
    return str(uuid.uuid4())


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    name: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default="idle")  # idle, thinking, executing, error, offline
    llm_backend: Mapped[str] = mapped_column(String(50), default="gemini")
    current_task: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_llm_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)   # full LLM response
    is_llm_real: Mapped[bool] = mapped_column(Boolean, default=False)             # True = real API call
    cpu_percent: Mapped[float] = mapped_column(Float, default=0.0)
    memory_mb: Mapped[float] = mapped_column(Float, default=128.0)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    tasks_completed: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    color: Mapped[str] = mapped_column(String(20), default="#FFD700")
    icon: Mapped[str] = mapped_column(String(10), default="🤖")
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_active: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, decomposing, running, completed, failed
    priority: Mapped[int] = mapped_column(Integer, default=5)
    assigned_agent_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("agents.id"), nullable=True)
    dag: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # DAG workflow definition
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class GoalTask(Base):
    __tablename__ = "goal_tasks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    goal_id: Mapped[str] = mapped_column(String, ForeignKey("goals.id"))
    title: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    agent_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("agents.id"), nullable=True)
    depends_on: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MemoryEntry(Base):
    __tablename__ = "memory_entries"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    agent_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("agents.id"), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100), default="general")
    importance: Mapped[float] = mapped_column(Float, default=0.5)
    embedding: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON-serialized float list
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    access_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FederationNode(Base):
    __tablename__ = "federation_nodes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    name: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(100))
    ip_address: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="online")
    trust_score: Mapped[float] = mapped_column(Float, default=0.9)
    latency_ms: Mapped[float] = mapped_column(Float, default=50.0)
    agents_count: Mapped[int] = mapped_column(Integer, default=0)
    lat: Mapped[float] = mapped_column(Float, default=0.0)
    lng: Mapped[float] = mapped_column(Float, default=0.0)
    region: Mapped[str] = mapped_column(String(50), default="us-east")
    encrypted: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Plugin(Base):
    __tablename__ = "plugins"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(20), default="1.0.0")
    author: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(50))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    icon: Mapped[str] = mapped_column(String(10), default="🔌")
    downloads: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[float] = mapped_column(Float, default=4.5)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    type: Mapped[str] = mapped_column(String(100))
    source: Mapped[str] = mapped_column(String(100))
    message: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20), default="info")  # info, warning, error, success
    agent_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SwarmEdge(Base):
    __tablename__ = "swarm_edges"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_id)
    source_agent_id: Mapped[str] = mapped_column(String, ForeignKey("agents.id"))
    target_agent_id: Mapped[str] = mapped_column(String, ForeignKey("agents.id"))
    channel_type: Mapped[str] = mapped_column(String(50), default="direct")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    messages_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
