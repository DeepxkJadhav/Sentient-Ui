import customtkinter as ctk
import json, os, threading, time
from api_client import SentientAPI, SentientWebSocket
from components import *

theme_path = os.path.join(os.path.dirname(__file__), "theme.json")
config_path = os.path.join(os.path.dirname(__file__), "config.json")
ctk.set_default_color_theme(theme_path)
ctk.set_appearance_mode("Light")

class SentientUIApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sentient-UI — Native Core")
        self.geometry("1200x780")
        self.minsize(1000, 650)
        self.api = SentientAPI()
        self.config_data = self._load_config()
        self.backend_online = False
        self.telemetry = {}
        self.agents_data = []
        self.goals_data = []
        self.memory_data = []
        self.events_data = []

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=210, corner_radius=0, fg_color="#FAFAFA", border_width=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)
        self.sidebar.grid_propagate(False)

        logo = ctk.CTkLabel(self.sidebar, text="✦ Sentient-UI", font=ctk.CTkFont(size=20, weight="bold"), text_color=GOLD)
        logo.grid(row=0, column=0, padx=20, pady=(24, 6), sticky="w")
        ver = ctk.CTkLabel(self.sidebar, text="Native Core v1.0", font=ctk.CTkFont(size=10), text_color=TEXT_MUTED)
        ver.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        self.nav_buttons = {}
        pages = [("Dashboard", "📊", self.show_dashboard), ("Agents", "🤖", self.show_agents),
                 ("Goals", "🎯", self.show_goals), ("Memory", "🧠", self.show_memory),
                 ("Telemetry", "📈", self.show_telemetry), ("Settings", "⚙️", self.show_settings)]
        for i, (name, icon, cmd) in enumerate(pages):
            btn = ctk.CTkButton(self.sidebar, text=f"  {icon}  {name}", command=cmd,
                                fg_color="transparent", text_color=TEXT_PRIMARY, hover_color="#F0EDE4",
                                anchor="w", font=ctk.CTkFont(size=13), height=38, corner_radius=8)
            btn.grid(row=i+2, column=0, padx=12, pady=2, sticky="ew")
            self.nav_buttons[name] = btn

        self.status_label = ctk.CTkLabel(self.sidebar, text="● Offline", text_color=ERROR, font=ctk.CTkFont(size=11))
        self.status_label.grid(row=9, column=0, padx=20, pady=(0, 16), sticky="sw")

        # Main content
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=OFF_WHITE)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.content = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.content.grid(row=0, column=0, sticky="nsew", padx=20, pady=16)
        self.content.columnconfigure(0, weight=1)

        self.show_dashboard()
        self._start_polling()

    def _load_config(self):
        if os.path.exists(config_path):
            with open(config_path) as f: return json.load(f)
        return {"api_keys": {}, "plugins": {}, "ui_preferences": {"primary_color": "#D4AF37"}}

    def _save_config(self):
        with open(config_path, "w") as f: json.dump(self.config_data, f, indent=2)

    def _set_active(self, name):
        for n, btn in self.nav_buttons.items():
            btn.configure(fg_color=GOLD_LIGHT if n == name else "transparent",
                          text_color=GOLD_DARK if n == name else TEXT_PRIMARY)

    def _clear(self):
        for w in self.content.winfo_children(): w.destroy()

    def _start_polling(self):
        def poll():
            while True:
                try:
                    h = self.api.health()
                    self.backend_online = h is not None
                    if self.backend_online:
                        self.agents_data = self.api.list_agents() or []
                        self.goals_data = self.api.list_goals() or []
                        self.telemetry = self.api.telemetry_metrics() or {}
                        self.events_data = self.api.telemetry_events(15) or []
                    self.after(0, self._update_status)
                except: pass
                time.sleep(3)
        threading.Thread(target=poll, daemon=True).start()

    def _update_status(self):
        if self.backend_online:
            self.status_label.configure(text="● Backend Online", text_color=SUCCESS)
        else:
            self.status_label.configure(text="● Backend Offline", text_color=ERROR)

    # ═══════════════════ DASHBOARD ═══════════════════

    def show_dashboard(self):
        self._clear(); self._set_active("Dashboard")
        SectionHeader(self.content, "Mission Control").grid(row=0, column=0, sticky="ew", pady=(0,16))

        kpi_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        kpi_frame.grid(row=1, column=0, sticky="ew", pady=(0,16))
        for i in range(4): kpi_frame.columnconfigure(i, weight=1)

        ov = self.api.system_overview() or {}
        cards = [
            ("Total Agents", str(ov.get("agents",{}).get("total", len(self.agents_data))), "Active runtime", GOLD),
            ("Memory Entries", str(ov.get("memory",{}).get("total",0)), "Vector store", CYAN),
            ("Active Goals", str(ov.get("goals",{}).get("total",0)), "In DAG planner", PURPLE),
            ("Swarm Channels", str(ov.get("swarm",{}).get("active_channels",0)), f"{ov.get('swarm',{}).get('messages_per_sec',0)} msg/s", SUCCESS),
        ]
        for i,(t,v,s,c) in enumerate(cards):
            KPICard(kpi_frame, t, v, s, c).grid(row=0, column=i, padx=6, sticky="ew")

        # System vitals
        sys_data = ov.get("system", {})
        vitals = ctk.CTkFrame(self.content, fg_color=WHITE, corner_radius=10, border_width=1, border_color=LIGHT_GRAY)
        vitals.grid(row=2, column=0, sticky="ew", pady=(0,16))
        vitals.columnconfigure(0, weight=1)
        ctk.CTkLabel(vitals, text="System Vitals", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_PRIMARY).grid(row=0, column=0, padx=16, pady=(12,8), sticky="w")
        for i,(lbl,val,clr) in enumerate([
            ("CPU", sys_data.get("cpu_percent",0), GOLD),
            ("Memory", sys_data.get("memory_percent",0), CYAN),
            ("GPU", sys_data.get("gpu_percent",0), PURPLE)]):
            LabeledProgress(vitals, lbl, val, clr).grid(row=i+1, column=0, padx=16, pady=4, sticky="ew")
        ctk.CTkFrame(vitals, height=8, fg_color="transparent").grid(row=5)  # spacer

        # Events
        ev_frame = ctk.CTkFrame(self.content, fg_color=WHITE, corner_radius=10, border_width=1, border_color=LIGHT_GRAY)
        ev_frame.grid(row=3, column=0, sticky="ew")
        ev_frame.columnconfigure(0, weight=1)
        ctk.CTkLabel(ev_frame, text="Recent Events", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_PRIMARY).grid(row=0, column=0, padx=16, pady=(12,4), sticky="w")
        for i, ev in enumerate(self.events_data[:10]):
            EventRow(ev_frame, ev.get("message",""), ev.get("severity","info")).grid(
                row=i+1, column=0, sticky="ew", padx=12, pady=1)
        if not self.events_data:
            ctk.CTkLabel(ev_frame, text="No events yet — start the backend", text_color=TEXT_MUTED,
                         font=ctk.CTkFont(size=11)).grid(row=1, column=0, padx=16, pady=12)
        ctk.CTkFrame(ev_frame, height=8, fg_color="transparent").grid(row=20)

    # ═══════════════════ AGENTS ═══════════════════

    def show_agents(self):
        self._clear(); self._set_active("Agents")
        SectionHeader(self.content, "Agent Runtime", "＋ New Agent", self._create_agent_dialog).grid(
            row=0, column=0, sticky="ew", pady=(0,16))

        if not self.agents_data:
            ctk.CTkLabel(self.content, text="No agents found. Start backend or create one.",
                         text_color=TEXT_MUTED, font=ctk.CTkFont(size=13)).grid(row=1, column=0, pady=40)
            return
        for i, agent in enumerate(self.agents_data):
            AgentListItem(self.content, agent).grid(row=i+1, column=0, sticky="ew", pady=3)

    def _create_agent_dialog(self):
        d = ctk.CTkToplevel(self); d.title("Create Agent"); d.geometry("400x340"); d.grab_set()
        d.configure(fg_color=OFF_WHITE)
        fields = {}
        for i,(lbl,ph) in enumerate([("Name","e.g. Scout-7"),("Role","e.g. researcher"),
                                      ("LLM Backend","gemini / openai / claude")]):
            ctk.CTkLabel(d, text=lbl, font=ctk.CTkFont(size=12)).grid(row=i, column=0, padx=20, pady=(16 if i==0 else 8, 0), sticky="w")
            e = ctk.CTkEntry(d, placeholder_text=ph, width=340)
            e.grid(row=i, column=0, padx=20, pady=(40 if i==0 else 32, 0), sticky="w")
            fields[lbl.lower().replace(" ","_")] = e
        def submit():
            self.api.create_agent({"name": fields["name"].get(), "role": fields["role"].get(),
                                   "llm_backend": fields["llm_backend"].get() or "gemini"})
            d.destroy(); self.agents_data = self.api.list_agents() or []; self.show_agents()
        ctk.CTkButton(d, text="Create Agent", command=submit, fg_color=GOLD, hover_color=GOLD_DARK,
                      text_color=WHITE).grid(row=4, column=0, padx=20, pady=24, sticky="ew")

    # ═══════════════════ GOALS ═══════════════════

    def show_goals(self):
        self._clear(); self._set_active("Goals")
        SectionHeader(self.content, "Goal Planner", "＋ New Goal", self._create_goal_dialog).grid(
            row=0, column=0, sticky="ew", pady=(0,16))

        if not self.goals_data:
            ctk.CTkLabel(self.content, text="No goals found.", text_color=TEXT_MUTED,
                         font=ctk.CTkFont(size=13)).grid(row=1, column=0, pady=40)
            return
        for i, goal in enumerate(self.goals_data):
            GoalListItem(self.content, goal).grid(row=i+1, column=0, sticky="ew", pady=3)

    def _create_goal_dialog(self):
        d = ctk.CTkToplevel(self); d.title("Create Goal"); d.geometry("450x300"); d.grab_set()
        d.configure(fg_color=OFF_WHITE)
        ctk.CTkLabel(d, text="Goal Title", font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=20, pady=(16,0), sticky="w")
        title_e = ctk.CTkEntry(d, placeholder_text="e.g. Research market trends", width=400)
        title_e.grid(row=1, column=0, padx=20, pady=(4,0), sticky="w")
        ctk.CTkLabel(d, text="Description", font=ctk.CTkFont(size=12)).grid(row=2, column=0, padx=20, pady=(12,0), sticky="w")
        desc_e = ctk.CTkTextbox(d, width=400, height=80)
        desc_e.grid(row=3, column=0, padx=20, pady=(4,0), sticky="w")
        def submit():
            self.api.create_goal({"title": title_e.get(), "description": desc_e.get("1.0","end").strip()})
            d.destroy(); self.goals_data = self.api.list_goals() or []; self.show_goals()
        ctk.CTkButton(d, text="Create Goal", command=submit, fg_color=GOLD, hover_color=GOLD_DARK,
                      text_color=WHITE).grid(row=4, column=0, padx=20, pady=16, sticky="ew")

    # ═══════════════════ MEMORY ═══════════════════

    def show_memory(self):
        self._clear(); self._set_active("Memory")
        SectionHeader(self.content, "Memory Explorer", "＋ Add Memory", self._create_memory_dialog).grid(
            row=0, column=0, sticky="ew", pady=(0,8))

        # Search
        search_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0,12))
        search_frame.columnconfigure(0, weight=1)
        self._mem_search = ctk.CTkEntry(search_frame, placeholder_text="Search memory vectors...", height=36)
        self._mem_search.grid(row=0, column=0, sticky="ew", padx=(0,8))
        ctk.CTkButton(search_frame, text="Search", width=80, height=36, fg_color=GOLD,
                      hover_color=GOLD_DARK, text_color=WHITE, command=self._search_memory).grid(row=0, column=1)

        self.memory_data = self.api.list_memory(30) or []
        if not self.memory_data:
            ctk.CTkLabel(self.content, text="No memory entries.", text_color=TEXT_MUTED,
                         font=ctk.CTkFont(size=13)).grid(row=2, column=0, pady=40)
            return
        for i, entry in enumerate(self.memory_data):
            MemoryCard(self.content, entry).grid(row=i+2, column=0, sticky="ew", pady=3)

    def _search_memory(self):
        q = self._mem_search.get().strip()
        if q:
            results = self.api.search_memory(q) or []
            # Re-render with results
            for w in list(self.content.winfo_children())[2:]: w.destroy()
            for i, entry in enumerate(results):
                MemoryCard(self.content, entry).grid(row=i+2, column=0, sticky="ew", pady=3)

    def _create_memory_dialog(self):
        d = ctk.CTkToplevel(self); d.title("Add Memory"); d.geometry("450x350"); d.grab_set()
        d.configure(fg_color=OFF_WHITE)
        ctk.CTkLabel(d, text="Content", font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=20, pady=(16,0), sticky="w")
        content_e = ctk.CTkTextbox(d, width=400, height=100)
        content_e.grid(row=1, column=0, padx=20, pady=(4,0))
        ctk.CTkLabel(d, text="Category", font=ctk.CTkFont(size=12)).grid(row=2, column=0, padx=20, pady=(12,0), sticky="w")
        cat_e = ctk.CTkEntry(d, placeholder_text="general", width=400)
        cat_e.grid(row=3, column=0, padx=20, pady=(4,0))
        def submit():
            self.api.create_memory({"content": content_e.get("1.0","end").strip(),
                                    "category": cat_e.get() or "general"})
            d.destroy(); self.show_memory()
        ctk.CTkButton(d, text="Save Memory", command=submit, fg_color=GOLD, hover_color=GOLD_DARK,
                      text_color=WHITE).grid(row=4, column=0, padx=20, pady=16, sticky="ew")

    # ═══════════════════ TELEMETRY ═══════════════════

    def show_telemetry(self):
        self._clear(); self._set_active("Telemetry")
        SectionHeader(self.content, "Live Telemetry").grid(row=0, column=0, sticky="ew", pady=(0,16))

        m = self.telemetry or {}
        kpi_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        kpi_frame.grid(row=1, column=0, sticky="ew", pady=(0,16))
        for i in range(4): kpi_frame.columnconfigure(i, weight=1)
        metrics = [
            ("CPU", f"{m.get('cpu_percent','--')}%", GOLD),
            ("Memory", f"{m.get('memory_percent','--')}%", CYAN),
            ("GPU", f"{m.get('gpu_percent','--')}%", PURPLE),
            ("Tokens/s", str(m.get('tokens_per_sec','--')), WARNING),
        ]
        for i,(t,v,c) in enumerate(metrics):
            KPICard(kpi_frame, t, v, "", c, width=150).grid(row=0, column=i, padx=6, sticky="ew")

        # Latency
        lat_frame = ctk.CTkFrame(self.content, fg_color=WHITE, corner_radius=10, border_width=1, border_color=LIGHT_GRAY)
        lat_frame.grid(row=2, column=0, sticky="ew", pady=(0,16))
        lat_frame.columnconfigure(0, weight=1)
        ctk.CTkLabel(lat_frame, text="Latency Percentiles", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_PRIMARY).grid(row=0, column=0, padx=16, pady=(12,8), sticky="w")
        for i,(lbl,key,clr) in enumerate([("P50","latency_p50",SUCCESS),("P95","latency_p95",GOLD),("P99","latency_p99",ERROR)]):
            val = m.get(key, 0)
            LabeledProgress(lat_frame, f"{lbl}: {val}ms", min(val/10, 100) if val else 0, clr).grid(
                row=i+1, column=0, padx=16, pady=4, sticky="ew")
        ctk.CTkFrame(lat_frame, height=8, fg_color="transparent").grid(row=5)

        # Events
        ev_frame = ctk.CTkFrame(self.content, fg_color=WHITE, corner_radius=10, border_width=1, border_color=LIGHT_GRAY)
        ev_frame.grid(row=3, column=0, sticky="ew")
        ev_frame.columnconfigure(0, weight=1)
        ctk.CTkLabel(ev_frame, text="Live Events", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_PRIMARY).grid(row=0, column=0, padx=16, pady=(12,4), sticky="w")
        for i, ev in enumerate(self.events_data[:12]):
            EventRow(ev_frame, ev.get("message",""), ev.get("severity","info")).grid(
                row=i+1, column=0, sticky="ew", padx=12, pady=1)
        ctk.CTkFrame(ev_frame, height=8, fg_color="transparent").grid(row=20)

    # ═══════════════════ SETTINGS ═══════════════════

    def show_settings(self):
        self._clear(); self._set_active("Settings")
        SectionHeader(self.content, "Settings & Configuration").grid(row=0, column=0, sticky="ew", pady=(0,16))

        tabview = ctk.CTkTabview(self.content, width=800, height=500, fg_color=WHITE,
                                  segmented_button_fg_color=LIGHT_GRAY, segmented_button_selected_color=GOLD,
                                  segmented_button_selected_hover_color=GOLD_DARK)
        tabview.grid(row=1, column=0, sticky="ew")

        tabview.add("API Keys"); tabview.add("System"); tabview.add("UI Theme")

        # === API Keys Tab ===
        keys_tab = tabview.tab("API Keys")
        providers = self.api.get_providers() or []
        self._key_entries = {}
        row = 0
        for p in providers[:8]:  # Show first 8
            pid = p.get("id","")
            f = ctk.CTkFrame(keys_tab, fg_color="transparent")
            f.grid(row=row, column=0, sticky="ew", padx=10, pady=4)
            f.columnconfigure(1, weight=1)
            ctk.CTkLabel(f, text=f"{p.get('icon','')} {p.get('name','')}", font=ctk.CTkFont(size=12),
                         text_color=TEXT_PRIMARY, width=180, anchor="w").grid(row=0, column=0, sticky="w")
            e = ctk.CTkEntry(f, placeholder_text=p.get("placeholder",""), show="•", height=32)
            e.grid(row=0, column=1, sticky="ew", padx=8)
            self._key_entries[pid] = e
            row += 1
        def save_keys():
            for pid, entry in self._key_entries.items():
                val = entry.get().strip()
                if val and not val.startswith("•"):
                    self.api.set_api_key(pid, val)
            Toast.show(self, "API keys saved!", 2000, SUCCESS)
        ctk.CTkButton(keys_tab, text="Save All Keys", command=save_keys, fg_color=GOLD,
                      hover_color=GOLD_DARK, text_color=WHITE).grid(row=row, column=0, padx=10, pady=16, sticky="w")

        # === System Tab ===
        sys_tab = tabview.tab("System")
        settings = self.api.get_settings() or {}
        sys_conf = settings.get("system", {})
        self._sys_entries = {}
        for i,(lbl,key,default) in enumerate([("Agent Tick Interval (s)","agent_tick_interval",2),
                                               ("Max Agents","max_agents",50),
                                               ("Memory Retention (days)","memory_retention_days",30)]):
            ctk.CTkLabel(sys_tab, text=lbl, font=ctk.CTkFont(size=12)).grid(row=i, column=0, padx=16, pady=8, sticky="w")
            e = ctk.CTkEntry(sys_tab, width=120, height=32)
            e.grid(row=i, column=1, padx=16, pady=8, sticky="w")
            e.insert(0, str(sys_conf.get(key, default)))
            self._sys_entries[key] = e
        def save_sys():
            data = {k: int(e.get()) for k,e in self._sys_entries.items() if e.get().isdigit()}
            self.api.update_system_settings(data)
            Toast.show(self, "System settings saved!", 2000, SUCCESS)
        ctk.CTkButton(sys_tab, text="Save Settings", command=save_sys, fg_color=GOLD,
                      hover_color=GOLD_DARK, text_color=WHITE).grid(row=4, column=0, padx=16, pady=16, sticky="w")

        # === UI Theme Tab ===
        ui_tab = tabview.tab("UI Theme")
        ctk.CTkLabel(ui_tab, text="Customize UI without code changes", text_color=TEXT_MUTED,
                     font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=16, pady=(12,12), sticky="w", columnspan=2)
        ctk.CTkLabel(ui_tab, text="Primary Accent (Hex):", font=ctk.CTkFont(size=12)).grid(
            row=1, column=0, padx=16, pady=8, sticky="w")
        self._color_entry = ctk.CTkEntry(ui_tab, width=150, height=32)
        self._color_entry.grid(row=1, column=1, padx=8, pady=8, sticky="w")
        self._color_entry.insert(0, self.config_data.get("ui_preferences",{}).get("primary_color","#D4AF37"))
        ctk.CTkLabel(ui_tab, text="Font Size:", font=ctk.CTkFont(size=12)).grid(
            row=2, column=0, padx=16, pady=8, sticky="w")
        self._font_slider = ctk.CTkSlider(ui_tab, from_=10, to=20, number_of_steps=10, width=200, progress_color=GOLD)
        self._font_slider.grid(row=2, column=1, padx=8, pady=8, sticky="w")
        self._font_slider.set(self.config_data.get("ui_preferences",{}).get("font_size",14))
        def apply_ui():
            new_color = self._color_entry.get().strip()
            self.config_data.setdefault("ui_preferences",{})["primary_color"] = new_color
            self.config_data["ui_preferences"]["font_size"] = int(self._font_slider.get())
            self._save_config()
            for btn in self.nav_buttons.values():
                btn.configure(hover_color=new_color+"20" if len(new_color)==7 else "#F0EDE4")
            Toast.show(self, "UI theme updated!", 2000, SUCCESS)
        ctk.CTkButton(ui_tab, text="Apply Changes", command=apply_ui, fg_color=GOLD,
                      hover_color=GOLD_DARK, text_color=WHITE).grid(row=3, column=0, padx=16, pady=16, sticky="w")

if __name__ == "__main__":
    app = SentientUIApp()
    app.mainloop()
