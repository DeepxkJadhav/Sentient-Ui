"""
Database configuration — SQLite with async SQLAlchemy
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///./sentient.db"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db():
    from models import Agent, Goal, MemoryEntry, FederationNode, Plugin, Event, SwarmEdge
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_initial_data()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def seed_initial_data():
    """Seed the database with initial agents, federation nodes, and plugins"""
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        from models import Agent, FederationNode, Plugin

        # Check if already seeded
        result = await db.execute(select(Agent))
        if result.scalars().first():
            return

        from constants import BUILT_IN_AGENTS, BUILT_IN_PLUGINS, BUILT_IN_NODES
        import json

        for agent_data in BUILT_IN_AGENTS:
            agent = Agent(**agent_data)
            db.add(agent)

        for node_data in BUILT_IN_NODES:
            node = FederationNode(**node_data)
            db.add(node)

        for plugin_data in BUILT_IN_PLUGINS:
            plugin = Plugin(**plugin_data)
            db.add(plugin)
        await db.commit()
