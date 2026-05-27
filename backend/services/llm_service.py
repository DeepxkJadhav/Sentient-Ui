"""
LLM Service — Routes agent prompts to real LLM providers.
Falls back to simulated tasks if no API key is configured.
"""
import json
import random
import asyncio
from pathlib import Path
from typing import Optional

import httpx

SETTINGS_FILE = Path(__file__).parent.parent / "settings.json"

# Provider configs: id → (base_url, model, header_style)
PROVIDER_CONFIG = {
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "model": "gpt-4o-mini",
        "style": "openai",
    },
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "meta-llama/llama-3.1-8b-instruct:free",
        "style": "openai",
    },
    "anthropic": {
        "url": "https://api.anthropic.com/v1/messages",
        "model": "claude-haiku-20240307",
        "style": "anthropic",
    },
    "google_ai": {
        "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
        "model": "gemini-1.5-flash",
        "style": "gemini",
    },
    # Agents labelled "gemini" use google_ai key
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
        "model": "gemini-1.5-flash",
        "style": "gemini",
    },
    # Agents labelled "claude" use anthropic key
    "claude": {
        "url": "https://api.anthropic.com/v1/messages",
        "model": "claude-haiku-20240307",
        "style": "anthropic",
    },
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama3-8b-8192",
        "style": "openai",
    },
    "mistral": {
        "url": "https://api.mistral.ai/v1/chat/completions",
        "model": "mistral-small-latest",
        "style": "openai",
    },
}

# Maps agent llm_backend → which settings.json key to look up
BACKEND_TO_KEY = {
    "openai": "openai",
    "claude": "anthropic",
    "gemini": "google_ai",
    "ollama": None,   # local, no key needed
    "groq": "groq",
    "mistral": "mistral",
}

FALLBACK_TASKS = [
    "Analyzing codebase structure for architectural patterns",
    "Optimizing database query performance",
    "Generating API documentation",
    "Running security vulnerability scan",
    "Deploying containerized microservice",
    "Training classification model on dataset",
    "Writing unit tests for authentication module",
    "Decomposing complex goal into subtasks",
    "Researching competitor API integrations",
    "Refactoring legacy authentication system",
    "Debugging memory leak in event processor",
    "Optimizing vector index for semantic search",
    "Reviewing PR for security issues",
    "Setting up CI/CD pipeline configuration",
    "Analyzing user behavior telemetry data",
]


def _load_api_keys() -> dict:
    try:
        if SETTINGS_FILE.exists():
            data = json.loads(SETTINGS_FILE.read_text())
            return data.get("api_keys", {})
    except Exception:
        pass
    return {}


def _get_api_key(backend: str) -> Optional[str]:
    keys = _load_api_keys()
    settings_key = BACKEND_TO_KEY.get(backend)
    if settings_key is None:
        return None
    return keys.get(settings_key) or None


def _build_prompt(agent_name: str, role: str, status: str) -> str:
    action = "thinking about what to work on next" if status == "thinking" else "actively executing a task"
    return (
        f"You are {agent_name}, an autonomous AI agent with the role of {role}. "
        f"You are currently {action}. "
        f"Respond with exactly ONE short sentence (max 12 words) describing the specific technical task you are working on right now. "
        f"Be concrete and technical. Do NOT include any preamble, quotes, or explanation — just the task sentence."
    )


async def _call_openai(url: str, model: str, api_key: str, prompt: str) -> str:
    # Auto-detect OpenRouter keys
    if api_key.startswith("sk-or-"):
        url = "https://openrouter.ai/api/v1/chat/completions"
        model = "meta-llama/llama-3.1-8b-instruct:free"
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 60,
                "temperature": 0.9,
            },
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()


async def _call_anthropic(url: str, model: str, api_key: str, prompt: str) -> str:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            url,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": 60,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        resp.raise_for_status()
        return resp.json()["content"][0]["text"].strip()


async def _call_gemini(url: str, api_key: str, prompt: str) -> str:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{url}?key={api_key}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": 60, "temperature": 0.9},
            },
        )
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()


async def get_agent_task(agent_name: str, role: str, backend: str, status: str) -> tuple[str, bool]:
    """
    Returns (task_description, is_real_llm).
    Falls back to a random simulated task if no key / API error.
    """
    api_key = _get_api_key(backend)

    # Ollama — local, call directly (no key)
    if backend == "ollama":
        try:
            prompt = _build_prompt(agent_name, role, status)
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(
                    "http://localhost:11434/api/generate",
                    json={"model": "llama3", "prompt": prompt, "stream": False},
                )
                resp.raise_for_status()
                text = resp.json().get("response", "").strip()
                if text:
                    return text[:200], True
        except Exception:
            pass
        return random.choice(FALLBACK_TASKS), False

    if not api_key:
        return random.choice(FALLBACK_TASKS), False

    cfg = PROVIDER_CONFIG.get(backend)
    if not cfg:
        return random.choice(FALLBACK_TASKS), False

    prompt = _build_prompt(agent_name, role, status)

    try:
        style = cfg["style"]
        if style == "openai":
            text = await _call_openai(cfg["url"], cfg["model"], api_key, prompt)
        elif style == "anthropic":
            text = await _call_anthropic(cfg["url"], cfg["model"], api_key, prompt)
        elif style == "gemini":
            text = await _call_gemini(cfg["url"], api_key, prompt)
        else:
            return random.choice(FALLBACK_TASKS), False

        # Clean up any leading/trailing punctuation the model sometimes adds
        text = text.strip('"\'').strip()
        if text:
            return text[:200], True

    except Exception as e:
        print(f"[LLM] {backend} call failed for {agent_name}: {e}", flush=True)

    return random.choice(FALLBACK_TASKS), False
