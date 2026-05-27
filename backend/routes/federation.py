"""Federation routes"""
import random
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import FederationNode

router = APIRouter()


@router.get("/")
async def list_nodes(db: AsyncSession = Depends(get_db)):
    nodes = (await db.execute(select(FederationNode))).scalars().all()
    return [_node_dict(n) for n in nodes]


@router.get("/audit")
async def audit_trail(db: AsyncSession = Depends(get_db)):
    from models import Event
    events = (await db.execute(
        select(Event).order_by(Event.created_at.desc()).limit(30)
    )).scalars().all()
    return [{"id": e.id, "type": e.type, "source": e.source, "message": e.message, "severity": e.severity, "ts": e.created_at.isoformat()} for e in events]


@router.get("/trust-matrix")
async def trust_matrix(db: AsyncSession = Depends(get_db)):
    nodes = (await db.execute(select(FederationNode))).scalars().all()
    matrix = {}
    for n1 in nodes:
        matrix[n1.name] = {}
        for n2 in nodes:
            if n1.id == n2.id:
                matrix[n1.name][n2.name] = 1.0
            else:
                matrix[n1.name][n2.name] = round(min(n1.trust_score, n2.trust_score) * random.uniform(0.85, 1.0), 3)
    return matrix


def _node_dict(node: FederationNode) -> dict:
    return {
        "id": node.id,
        "name": node.name,
        "location": node.location,
        "ip_address": node.ip_address,
        "status": node.status,
        "trust_score": node.trust_score,
        "latency_ms": round(node.latency_ms + random.uniform(-5, 10), 1),
        "agents_count": node.agents_count,
        "lat": node.lat,
        "lng": node.lng,
        "region": node.region,
        "encrypted": node.encrypted,
    }
