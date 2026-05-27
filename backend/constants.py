"""
Constants — Built-in agents, plugins, federation nodes
"""
import uuid

BUILT_IN_AGENTS = [
    {"id": str(uuid.uuid4()), "name": "Architect", "role": "Code Architect", "llm_backend": "gemini", "color": "#FFD700", "icon": "🏗️", "status": "idle", "is_builtin": True},
    {"id": str(uuid.uuid4()), "name": "Nexus", "role": "Backend Engineer", "llm_backend": "openai", "color": "#00D4FF", "icon": "⚙️", "status": "idle", "is_builtin": True},
    {"id": str(uuid.uuid4()), "name": "Prism", "role": "Frontend Engineer", "llm_backend": "claude", "color": "#8B5CF6", "icon": "🎨", "status": "idle", "is_builtin": True},
    {"id": str(uuid.uuid4()), "name": "Shield", "role": "Security Auditor", "llm_backend": "gemini", "color": "#FF4444", "icon": "🛡️", "status": "idle", "is_builtin": True},
    {"id": str(uuid.uuid4()), "name": "Forge", "role": "DevOps Agent", "llm_backend": "ollama", "color": "#FF8C00", "icon": "🔥", "status": "idle", "is_builtin": True},
    {"id": str(uuid.uuid4()), "name": "Synapse", "role": "ML Engineer", "llm_backend": "openai", "color": "#00FF88", "icon": "🧠", "status": "idle", "is_builtin": True},
    {"id": str(uuid.uuid4()), "name": "Probe", "role": "Testing Agent", "llm_backend": "gemini", "color": "#FF69B4", "icon": "🔬", "status": "idle", "is_builtin": True},
    {"id": str(uuid.uuid4()), "name": "Oracle", "role": "Planner Agent", "llm_backend": "claude", "color": "#FFD700", "icon": "🎯", "status": "idle", "is_builtin": True},
    {"id": str(uuid.uuid4()), "name": "Scout", "role": "Research Agent", "llm_backend": "gemini", "color": "#40E0D0", "icon": "🔍", "status": "idle", "is_builtin": True},
    {"id": str(uuid.uuid4()), "name": "Scribe", "role": "Documentation Agent", "llm_backend": "claude", "color": "#DDA0DD", "icon": "📝", "status": "idle", "is_builtin": True},
    {"id": str(uuid.uuid4()), "name": "Specter", "role": "Debugging Agent", "llm_backend": "openai", "color": "#98FB98", "icon": "👁️", "status": "idle", "is_builtin": True},
    {"id": str(uuid.uuid4()), "name": "Atlas", "role": "Database Optimizer", "llm_backend": "ollama", "color": "#F0E68C", "icon": "🗄️", "status": "idle", "is_builtin": True},
]

BUILT_IN_NODES = [
    {"id": str(uuid.uuid4()), "name": "Local Primary", "location": "San Francisco, CA", "ip_address": "192.168.1.1", "status": "online", "trust_score": 1.0, "latency_ms": 2.1, "agents_count": 12, "lat": 37.7749, "lng": -122.4194, "region": "us-west", "encrypted": True},
    {"id": str(uuid.uuid4()), "name": "AWS US-East", "location": "Virginia, USA", "ip_address": "54.162.xxx.xxx", "status": "online", "trust_score": 0.98, "latency_ms": 45.2, "agents_count": 8, "lat": 37.4316, "lng": -78.6569, "region": "us-east", "encrypted": True},
    {"id": str(uuid.uuid4()), "name": "GCP Europe West", "location": "Frankfurt, DE", "ip_address": "34.89.xxx.xxx", "status": "online", "trust_score": 0.97, "latency_ms": 120.5, "agents_count": 5, "lat": 50.1109, "lng": 8.6821, "region": "eu-west", "encrypted": True},
    {"id": str(uuid.uuid4()), "name": "Azure Asia Pacific", "location": "Singapore", "ip_address": "40.90.xxx.xxx", "status": "online", "trust_score": 0.95, "latency_ms": 180.3, "agents_count": 4, "lat": 1.3521, "lng": 103.8198, "region": "ap-south", "encrypted": True},
    {"id": str(uuid.uuid4()), "name": "Edge Node Tokyo", "location": "Tokyo, Japan", "ip_address": "13.230.xxx.xxx", "status": "online", "trust_score": 0.93, "latency_ms": 160.7, "agents_count": 3, "lat": 35.6762, "lng": 139.6503, "region": "ap-north", "encrypted": True},
    {"id": str(uuid.uuid4()), "name": "Enterprise Cluster", "location": "London, UK", "ip_address": "185.231.xxx.xxx", "status": "degraded", "trust_score": 0.88, "latency_ms": 95.4, "agents_count": 6, "lat": 51.5074, "lng": -0.1278, "region": "eu-north", "encrypted": True},
]

BUILT_IN_PLUGINS = [
    {"id": str(uuid.uuid4()), "name": "Web Scraper Pro", "description": "High-performance web scraping with JS rendering support", "version": "2.3.1", "author": "SentientLabs", "category": "tools", "enabled": True, "icon": "🕷️", "downloads": 12847, "rating": 4.8},
    {"id": str(uuid.uuid4()), "name": "GitHub Connector", "description": "Deep GitHub integration: PRs, issues, code review automation", "version": "1.8.0", "author": "SentientLabs", "category": "integration", "enabled": True, "icon": "🐙", "downloads": 9234, "rating": 4.9},
    {"id": str(uuid.uuid4()), "name": "Slack Notifier", "description": "Real-time agent event notifications to Slack channels", "version": "1.2.0", "author": "Community", "category": "communication", "enabled": True, "icon": "💬", "downloads": 7891, "rating": 4.6},
    {"id": str(uuid.uuid4()), "name": "SQL Executor", "description": "Secure SQL query execution with parameterization and sandboxing", "version": "3.1.0", "author": "SentientLabs", "category": "tools", "enabled": True, "icon": "🗃️", "downloads": 6543, "rating": 4.7},
    {"id": str(uuid.uuid4()), "name": "Docker Manager", "description": "Spawn and manage Docker containers from agent workflows", "version": "1.5.2", "author": "DevOps Guild", "category": "infrastructure", "enabled": False, "icon": "🐳", "downloads": 5432, "rating": 4.5},
    {"id": str(uuid.uuid4()), "name": "PDF Analyzer", "description": "Extract, analyze, and embed content from PDF documents", "version": "2.0.1", "author": "Community", "category": "tools", "enabled": True, "icon": "📄", "downloads": 4321, "rating": 4.4},
    {"id": str(uuid.uuid4()), "name": "Email Automation", "description": "SMTP/IMAP email automation with template engine", "version": "1.1.0", "author": "SentientLabs", "category": "communication", "enabled": False, "icon": "📧", "downloads": 3876, "rating": 4.3},
    {"id": str(uuid.uuid4()), "name": "Crypto Oracle", "description": "Real-time crypto market data and trading signal analysis", "version": "0.9.5", "author": "FinTech Guild", "category": "analytics", "enabled": False, "icon": "₿", "downloads": 2987, "rating": 4.1},
]

AGENT_TASKS = [
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
    "Reviewing PR #247 for security issues",
    "Setting up CI/CD pipeline configuration",
    "Analyzing user behavior telemetry data",
    "Generating synthetic training data",
    "Auditing dependency versions for CVEs",
    "Profiling CPU usage in hot code paths",
    "Migrating schema to new data model",
    "Implementing rate limiting middleware",
]

LLM_BACKENDS = ["openai", "claude", "gemini", "ollama"]
