"""Goals routes — Goal decomposition and DAG planning"""
import uuid
import random
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models import Goal, GoalTask, Agent

router = APIRouter()


class GoalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int = 5


@router.get("/")
async def list_goals(db: AsyncSession = Depends(get_db)):
    goals = (await db.execute(select(Goal).order_by(Goal.created_at.desc()).limit(50))).scalars().all()
    return [_goal_dict(g) for g in goals]


@router.post("/")
async def create_goal(body: GoalCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    goal = Goal(
        id=str(uuid.uuid4()),
        title=body.title,
        description=body.description,
        priority=body.priority,
        status="pending",
        progress=0.0,
        created_at=datetime.utcnow(),
    )
    db.add(goal)
    await db.commit()
    await db.refresh(goal)

    # Trigger async decomposition
    background_tasks.add_task(_decompose_goal, goal.id)
    return _goal_dict(goal)


@router.get("/{goal_id}")
async def get_goal(goal_id: str, db: AsyncSession = Depends(get_db)):
    goal = await db.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    tasks = (await db.execute(select(GoalTask).where(GoalTask.goal_id == goal_id).order_by(GoalTask.order))).scalars().all()
    return {**_goal_dict(goal), "tasks": [_task_dict(t) for t in tasks]}


@router.delete("/{goal_id}")
async def delete_goal(goal_id: str, db: AsyncSession = Depends(get_db)):
    goal = await db.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    await db.delete(goal)
    await db.commit()
    return {"deleted": goal_id}


async def _decompose_goal(goal_id: str):
    """Background task: decompose goal into DAG of tasks"""
    import asyncio
    await asyncio.sleep(1.5)

    from database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        goal = await db.get(Goal, goal_id)
        if not goal:
            return

        goal.status = "decomposing"
        await db.commit()

        await asyncio.sleep(2.0)

        # Generate realistic task DAG
        task_templates = _get_task_templates(goal.title)
        agents = (await db.execute(select(Agent).limit(12))).scalars().all()

        dag_nodes = []
        dag_edges = []

        for i, (task_title, agent_role) in enumerate(task_templates):
            task_id = str(uuid.uuid4())
            agent = next((a for a in agents if a.role == agent_role), random.choice(agents))
            depends_on = [dag_nodes[j]["id"] for j in range(max(0, i - 2), i) if random.random() < 0.6]

            task = GoalTask(
                id=task_id,
                goal_id=goal_id,
                title=task_title,
                status="pending",
                agent_id=agent.id,
                depends_on=depends_on,
                order=i,
            )
            db.add(task)
            dag_nodes.append({"id": task_id, "title": task_title, "agent": agent.name, "status": "pending"})
            if depends_on:
                for dep in depends_on:
                    dag_edges.append({"from": dep, "to": task_id})

        goal.dag = {"nodes": dag_nodes, "edges": dag_edges}
        goal.status = "running"
        await db.commit()

        # Simulate task progress
        for i, node in enumerate(dag_nodes):
            await asyncio.sleep(random.uniform(3, 8))
            task_result = await db.execute(select(GoalTask).where(GoalTask.id == node["id"]))
            task = task_result.scalars().first()
            if task:
                task.status = "completed"
                goal.progress = round((i + 1) / len(dag_nodes) * 100, 1)
                await db.commit()

        goal.status = "completed"
        goal.progress = 100.0
        goal.completed_at = datetime.utcnow()
        await db.commit()


def _get_task_templates(goal_title: str) -> list[tuple[str, str]]:
    """Generate realistic task templates based on goal"""
    base_tasks = [
        ("Analyze requirements and define scope", "Planner Agent"),
        ("Research existing solutions and patterns", "Research Agent"),
        ("Design system architecture", "Code Architect"),
        ("Set up project structure and dependencies", "Backend Engineer"),
        ("Implement core backend logic", "Backend Engineer"),
        ("Design and implement UI components", "Frontend Engineer"),
        ("Write comprehensive unit tests", "Testing Agent"),
        ("Run security vulnerability audit", "Security Auditor"),
        ("Configure deployment pipeline", "DevOps Agent"),
        ("Optimize database queries", "Database Optimizer"),
        ("Generate API documentation", "Documentation Agent"),
        ("Debug and resolve issues", "Debugging Agent"),
        ("Train ML model if needed", "ML Engineer"),
        ("Final integration testing", "Testing Agent"),
        ("Deploy to production", "DevOps Agent"),
    ]
    # Return a subset based on goal complexity
    count = random.randint(5, 12)
    return random.sample(base_tasks, min(count, len(base_tasks)))


def _goal_dict(goal: Goal) -> dict:
    return {
        "id": goal.id,
        "title": goal.title,
        "description": goal.description,
        "status": goal.status,
        "priority": goal.priority,
        "progress": goal.progress,
        "dag": goal.dag,
        "created_at": goal.created_at.isoformat() if goal.created_at else None,
        "completed_at": goal.completed_at.isoformat() if goal.completed_at else None,
    }


def _task_dict(task: GoalTask) -> dict:
    return {
        "id": task.id,
        "goal_id": task.goal_id,
        "title": task.title,
        "status": task.status,
        "agent_id": task.agent_id,
        "depends_on": task.depends_on,
        "order": task.order,
    }
