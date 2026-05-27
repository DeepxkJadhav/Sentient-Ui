"""
Sentient-UI API Client — Communicates with the FastAPI backend at localhost:8000
"""
import json
import threading
import time
import requests
import websocket

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"


class SentientAPI:
    """HTTP client for the Sentient-UI backend."""

    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.timeout = 5

    def _get(self, path):
        try:
            r = self.session.get(f"{self.base_url}{path}", timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"[API] GET {path} failed: {e}", flush=True)
            return None

    def _post(self, path, data=None):
        try:
            r = self.session.post(f"{self.base_url}{path}", json=data or {}, timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"[API] POST {path} failed: {e}", flush=True)
            return None

    def _delete(self, path):
        try:
            r = self.session.delete(f"{self.base_url}{path}", timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"[API] DELETE {path} failed: {e}", flush=True)
            return None

    # ─── Health ────────────────────────────────────
    def health(self):
        return self._get("/api/health")

    def system_overview(self):
        return self._get("/api/system/overview")

    # ─── Agents ────────────────────────────────────
    def list_agents(self):
        return self._get("/api/agents/") or []

    def get_agent(self, agent_id):
        return self._get(f"/api/agents/{agent_id}")

    def create_agent(self, data):
        return self._post("/api/agents/", data)

    def delete_agent(self, agent_id):
        return self._delete(f"/api/agents/{agent_id}")

    # ─── Goals ─────────────────────────────────────
    def list_goals(self):
        return self._get("/api/goals/") or []

    def create_goal(self, data):
        return self._post("/api/goals/", data)

    def delete_goal(self, goal_id):
        return self._delete(f"/api/goals/{goal_id}")

    # ─── Memory ────────────────────────────────────
    def list_memory(self, limit=50):
        return self._get(f"/api/memory/?limit={limit}") or []

    def search_memory(self, query):
        return self._post("/api/memory/search", {"query": query}) or []

    def create_memory(self, data):
        return self._post("/api/memory/", data)

    # ─── Telemetry ─────────────────────────────────
    def telemetry_metrics(self):
        return self._get("/api/telemetry/metrics")

    def telemetry_history(self):
        return self._get("/api/telemetry/history") or []

    def telemetry_events(self, limit=30):
        return self._get(f"/api/telemetry/events?limit={limit}") or []

    # ─── Federation ────────────────────────────────
    def list_nodes(self):
        return self._get("/api/federation/") or []

    # ─── Swarm ─────────────────────────────────────
    def swarm_topology(self):
        return self._get("/api/swarm/topology")

    # ─── Settings ──────────────────────────────────
    def get_settings(self):
        return self._get("/api/settings/")

    def get_providers(self):
        return self._get("/api/settings/providers") or []

    def set_api_key(self, provider, key):
        return self._post("/api/settings/api-key", {"provider": provider, "key": key})

    def delete_api_key(self, provider):
        return self._delete(f"/api/settings/api-key/{provider}")

    def update_system_settings(self, data):
        return self._post("/api/settings/system", data)

    # ─── Plugins ───────────────────────────────────
    def list_plugins(self):
        return self._get("/api/plugins/") or []


class SentientWebSocket:
    """WebSocket client for real-time telemetry from the backend."""

    def __init__(self, url=WS_URL, on_message=None):
        self.url = url
        self.on_message_cb = on_message
        self.ws = None
        self.running = False
        self._thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass

    def _run(self):
        while self.running:
            try:
                self.ws = websocket.WebSocketApp(
                    self.url,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close,
                    on_open=self._on_open,
                )
                self.ws.run_forever(ping_interval=30, ping_timeout=10)
            except Exception as e:
                print(f"[WS] Connection error: {e}", flush=True)
            if self.running:
                time.sleep(3)  # Reconnect after delay

    def _on_open(self, ws):
        print("[WS] Connected", flush=True)

    def _on_message(self, ws, message):
        try:
            data = json.loads(message)
            if self.on_message_cb:
                self.on_message_cb(data)
        except Exception:
            pass

    def _on_error(self, ws, error):
        print(f"[WS] Error: {error}", flush=True)

    def _on_close(self, ws, code, msg):
        print(f"[WS] Closed: {code}", flush=True)

    def send_ping(self):
        if self.ws:
            try:
                self.ws.send("ping")
            except Exception:
                pass
