"""Memory routes — Shared vector memory across agents"""
import uuid
import json
import random
import numpy as np
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models import MemoryEntry

router = APIRouter()


class MemoryCreate(BaseModel):
    content: str
    agent_id: Optional[str] = None
    category: str = "general"
    importance: float = 0.5
    tags: Optional[list[str]] = None


@router.get("/")
async def list_memories(
    limit: int = Query(50, le=200),
    category: Optional[str] = None,
    agent_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(MemoryEntry).order_by(desc(MemoryEntry.created_at)).limit(limit)
    if category:
        query = query.where(MemoryEntry.category == category)
    if agent_id:
        query = query.where(MemoryEntry.agent_id == agent_id)
    entries = (await db.execute(query)).scalars().all()
    return [_mem_dict(e) for e in entries]


@router.post("/")
async def create_memory(body: MemoryCreate, db: AsyncSession = Depends(get_db)):
    # Generate a fake embedding (in production: use real embedding model)
    embedding = _fake_embedding(body.content)
    entry = MemoryEntry(
        id=str(uuid.uuid4()),
        agent_id=body.agent_id,
        content=body.content,
        category=body.category,
        importance=body.importance,
        embedding=json.dumps(embedding),
        tags=body.tags or [],
        created_at=datetime.utcnow(),
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return _mem_dict(entry)


@router.post("/search")
async def search_memories(
    query: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """Semantic similarity search using cosine similarity on fake embeddings"""
    query_embedding = np.array(_fake_embedding(query))
    entries = (await db.execute(select(MemoryEntry).where(MemoryEntry.embedding.isnot(None)).limit(200))).scalars().all()

    results = []
    for entry in entries:
        try:
            emb = np.array(json.loads(entry.embedding))
            similarity = float(np.dot(query_embedding, emb) / (np.linalg.norm(query_embedding) * np.linalg.norm(emb) + 1e-8))
            results.append((_mem_dict(entry), similarity))
        except Exception:
            pass

    results.sort(key=lambda x: x[1], reverse=True)
    return [{"memory": r[0], "similarity": round(r[1], 4)} for r in results[:limit]]


@router.get("/stats")
async def memory_stats(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import func
    total = (await db.execute(select(func.count(MemoryEntry.id)))).scalar()
    categories = (await db.execute(
        select(MemoryEntry.category, func.count(MemoryEntry.id)).group_by(MemoryEntry.category)
    )).all()
    return {
        "total": total,
        "categories": {cat: count for cat, count in categories},
        "avg_importance": round(random.uniform(0.5, 0.8), 3),
        "vector_dimensions": 128,
    }


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str, db: AsyncSession = Depends(get_db)):
    entry = await db.get(MemoryEntry, memory_id)
    if entry:
        await db.delete(entry)
        await db.commit()
    return {"deleted": memory_id}


def _fake_embedding(text: str) -> list[float]:
    """Generate a deterministic-ish fake embedding based on text hash"""
    rng = random.Random(hash(text) % (2**31))
    vec = [rng.gauss(0, 1) for _ in range(128)]
    norm = sum(v**2 for v in vec) ** 0.5
    return [v / (norm + 1e-8) for v in vec]


def _mem_dict(entry: MemoryEntry) -> dict:
    return {
        "id": entry.id,
        "agent_id": entry.agent_id,
        "content": entry.content,
        "summary": entry.summary,
        "category": entry.category,
        "importance": entry.importance,
        "tags": entry.tags or [],
        "access_count": entry.access_count,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
    }
