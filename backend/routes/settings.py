"""Settings routes — API key storage and system configuration"""
import json
import os
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict

router = APIRouter()

SETTINGS_FILE = Path("./settings.json")

def load_settings() -> dict:
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text())
        except Exception:
            pass
    return {
        "api_keys": {},
        "llm_routing": {"default": "gemini", "fallback": "openai"},
        "system": {"agent_tick_interval": 2, "max_agents": 50, "memory_retention_days": 30},
        "integrations": {},
    }

def save_settings(data: dict):
    SETTINGS_FILE.write_text(json.dumps(data, indent=2))

class ApiKeyUpdate(BaseModel):
    provider: str
    key: str

class SystemSettings(BaseModel):
    agent_tick_interval: Optional[int] = None
    max_agents: Optional[int] = None
    memory_retention_days: Optional[int] = None
    default_llm: Optional[str] = None
    fallback_llm: Optional[str] = None

@router.get("/")
async def get_settings():
    data = load_settings()
    # Mask API keys for security
    masked = {}
    for provider, key in data.get("api_keys", {}).items():
        if key and len(key) > 8:
            masked[provider] = key[:4] + "●" * (len(key) - 8) + key[-4:]
        elif key:
            masked[provider] = "●" * len(key)
        else:
            masked[provider] = ""
    return {
        "api_keys": masked,
        "api_keys_configured": list(data.get("api_keys", {}).keys()),
        "llm_routing": data.get("llm_routing", {}),
        "system": data.get("system", {}),
    }

@router.post("/api-key")
async def set_api_key(body: ApiKeyUpdate):
    data = load_settings()
    if "api_keys" not in data:
        data["api_keys"] = {}
    data["api_keys"][body.provider] = body.key
    save_settings(data)
    return {"status": "saved", "provider": body.provider, "configured": bool(body.key)}

@router.delete("/api-key/{provider}")
async def delete_api_key(provider: str):
    data = load_settings()
    data.get("api_keys", {}).pop(provider, None)
    save_settings(data)
    return {"status": "deleted", "provider": provider}

@router.post("/system")
async def update_system_settings(body: SystemSettings):
    data = load_settings()
    if body.agent_tick_interval is not None:
        data.setdefault("system", {})["agent_tick_interval"] = body.agent_tick_interval
    if body.max_agents is not None:
        data.setdefault("system", {})["max_agents"] = body.max_agents
    if body.memory_retention_days is not None:
        data.setdefault("system", {})["memory_retention_days"] = body.memory_retention_days
    if body.default_llm is not None:
        data.setdefault("llm_routing", {})["default"] = body.default_llm
    if body.fallback_llm is not None:
        data.setdefault("llm_routing", {})["fallback"] = body.fallback_llm
    save_settings(data)
    return data.get("system", {})

@router.get("/providers")
async def get_providers():
    """Return all configurable API providers"""
    return [
        # LLM Providers
        {"id": "openai", "name": "OpenAI", "category": "llm", "icon": "🤖", "description": "GPT-4o, GPT-4 Turbo", "url": "https://platform.openai.com/api-keys", "placeholder": "sk-..."},
        {"id": "anthropic", "name": "Anthropic (Claude)", "category": "llm", "icon": "🧠", "description": "Claude 3.5 Sonnet, Claude 3 Opus", "url": "https://console.anthropic.com/", "placeholder": "sk-ant-..."},
        {"id": "google_ai", "name": "Google AI (Gemini)", "category": "llm", "icon": "✨", "description": "Gemini 1.5 Pro, Gemini Flash", "url": "https://aistudio.google.com/apikey", "placeholder": "AIza..."},
        {"id": "groq", "name": "Groq", "category": "llm", "icon": "⚡", "description": "Llama 3, Mixtral (ultra-fast inference)", "url": "https://console.groq.com/keys", "placeholder": "gsk_..."},
        {"id": "ollama", "name": "Ollama (Local)", "category": "llm", "icon": "🏠", "description": "Run models locally — no key needed", "url": "https://ollama.ai", "placeholder": "http://localhost:11434"},
        {"id": "mistral", "name": "Mistral AI", "category": "llm", "icon": "🌊", "description": "Mistral Large, Codestral", "url": "https://console.mistral.ai/", "placeholder": "..."},
        {"id": "cohere", "name": "Cohere", "category": "llm", "icon": "🔗", "description": "Command R+, Embed models", "url": "https://dashboard.cohere.com/", "placeholder": "..."},
        # Developer Tools
        {"id": "github", "name": "GitHub", "category": "developer", "icon": "🐙", "description": "Repos, PRs, Issues, Actions", "url": "https://github.com/settings/tokens", "placeholder": "ghp_..."},
        {"id": "gitlab", "name": "GitLab", "category": "developer", "icon": "🦊", "description": "Repos, MRs, CI/CD pipelines", "url": "https://gitlab.com/-/user_settings/personal_access_tokens", "placeholder": "glpat-..."},
        {"id": "jira", "name": "Jira", "category": "developer", "icon": "🎯", "description": "Issues, sprints, projects", "url": "https://id.atlassian.com/manage-profile/security/api-tokens", "placeholder": "..."},
        {"id": "linear", "name": "Linear", "category": "developer", "icon": "📐", "description": "Issues, projects, cycles", "url": "https://linear.app/settings/api", "placeholder": "lin_api_..."},
        {"id": "vercel", "name": "Vercel", "category": "developer", "icon": "▲", "description": "Deployments, projects, domains", "url": "https://vercel.com/account/tokens", "placeholder": "..."},
        {"id": "docker_hub", "name": "Docker Hub", "category": "developer", "icon": "🐳", "description": "Container registries, images", "url": "https://hub.docker.com/settings/security", "placeholder": "..."},
        {"id": "npm", "name": "npm Registry", "category": "developer", "icon": "📦", "description": "Publish packages, access registry", "url": "https://www.npmjs.com/settings/tokens", "placeholder": "npm_..."},
        # Google Services
        {"id": "google_gmail", "name": "Gmail", "category": "google", "icon": "📧", "description": "Send/read emails, drafts, labels", "url": "https://console.cloud.google.com/", "placeholder": "OAuth2 Client ID"},
        {"id": "google_calendar", "name": "Google Calendar", "category": "google", "icon": "📅", "description": "Events, scheduling, availability", "url": "https://console.cloud.google.com/", "placeholder": "OAuth2 Client ID"},
        {"id": "google_sheets", "name": "Google Sheets", "category": "google", "icon": "📊", "description": "Read/write spreadsheet data", "url": "https://console.cloud.google.com/", "placeholder": "OAuth2 Client ID"},
        {"id": "google_drive", "name": "Google Drive", "category": "google", "icon": "💾", "description": "Files, folders, sharing", "url": "https://console.cloud.google.com/", "placeholder": "OAuth2 Client ID"},
        {"id": "google_search", "name": "Google Search API", "category": "google", "icon": "🔍", "description": "Programmable search engine", "url": "https://programmablesearchengine.google.com/", "placeholder": "..."},
        # Communication
        {"id": "slack", "name": "Slack", "category": "communication", "icon": "💬", "description": "Messages, channels, workflows", "url": "https://api.slack.com/apps", "placeholder": "xoxb-..."},
        {"id": "discord", "name": "Discord", "category": "communication", "icon": "🎮", "description": "Messages, webhooks, bots", "url": "https://discord.com/developers/applications", "placeholder": "..."},
        {"id": "telegram", "name": "Telegram", "category": "communication", "icon": "✈️", "description": "Bot messages, groups", "url": "https://t.me/botfather", "placeholder": "bot_token:..."},
        {"id": "sendgrid", "name": "SendGrid", "category": "communication", "icon": "📨", "description": "Transactional email delivery", "url": "https://app.sendgrid.com/settings/api_keys", "placeholder": "SG...."},
        {"id": "twilio", "name": "Twilio", "category": "communication", "icon": "📱", "description": "SMS, calls, WhatsApp", "url": "https://console.twilio.com/", "placeholder": "ACxxx..."},
        # Data & Productivity
        {"id": "notion", "name": "Notion", "category": "productivity", "icon": "📝", "description": "Pages, databases, workspaces", "url": "https://www.notion.so/my-integrations", "placeholder": "secret_..."},
        {"id": "airtable", "name": "Airtable", "category": "productivity", "icon": "🗃️", "description": "Bases, tables, records", "url": "https://airtable.com/create/tokens", "placeholder": "pat..."},
        {"id": "hubspot", "name": "HubSpot", "category": "productivity", "icon": "🔶", "description": "CRM, contacts, deals", "url": "https://app.hubspot.com/", "placeholder": "..."},
        # Cloud & Infrastructure
        {"id": "aws", "name": "AWS", "category": "cloud", "icon": "☁️", "description": "S3, Lambda, EC2, RDS", "url": "https://console.aws.amazon.com/iam/", "placeholder": "AKIA..."},
        {"id": "gcp", "name": "Google Cloud", "category": "cloud", "icon": "🌐", "description": "GCS, Cloud Run, BigQuery", "url": "https://console.cloud.google.com/iam-admin/serviceaccounts", "placeholder": "JSON key"},
        {"id": "azure", "name": "Microsoft Azure", "category": "cloud", "icon": "🔷", "description": "Storage, Functions, Cosmos DB", "url": "https://portal.azure.com/", "placeholder": "..."},
        # Payments & Business
        {"id": "stripe", "name": "Stripe", "category": "business", "icon": "💳", "description": "Payments, subscriptions, webhooks", "url": "https://dashboard.stripe.com/apikeys", "placeholder": "sk_live_..."},
        {"id": "openweather", "name": "OpenWeather", "category": "data", "icon": "🌤️", "description": "Current weather & forecasts", "url": "https://openweathermap.org/api_keys", "placeholder": "..."},
        {"id": "serper", "name": "Serper (Web Search)", "category": "data", "icon": "🔎", "description": "Real-time web search API", "url": "https://serper.dev/api-key", "placeholder": "..."},
        {"id": "tavily", "name": "Tavily AI Search", "category": "data", "icon": "🕵️", "description": "AI-optimized web search", "url": "https://tavily.com/", "placeholder": "tvly-..."},
    ]
