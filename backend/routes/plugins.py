"""Plugins routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Plugin

router = APIRouter()


@router.get("/")
async def list_plugins(db: AsyncSession = Depends(get_db)):
    plugins = (await db.execute(select(Plugin).order_by(Plugin.downloads.desc()))).scalars().all()
    return [_plugin_dict(p) for p in plugins]


@router.patch("/{plugin_id}/toggle")
async def toggle_plugin(plugin_id: str, db: AsyncSession = Depends(get_db)):
    plugin = await db.get(Plugin, plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    plugin.enabled = not plugin.enabled
    await db.commit()
    return _plugin_dict(plugin)


def _plugin_dict(plugin: Plugin) -> dict:
    return {
        "id": plugin.id,
        "name": plugin.name,
        "description": plugin.description,
        "version": plugin.version,
        "author": plugin.author,
        "category": plugin.category,
        "enabled": plugin.enabled,
        "icon": plugin.icon,
        "downloads": plugin.downloads,
        "rating": plugin.rating,
    }
