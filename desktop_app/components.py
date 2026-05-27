"""
Sentient-UI Reusable UI Components — Gold & White CustomTkinter widgets
"""
import customtkinter as ctk
from typing import Optional, Callable


# ─── Color Constants ──────────────────────────────────────────────────────────

GOLD = "#D4AF37"
GOLD_DARK = "#B8960C"
GOLD_LIGHT = "#F5E6A3"
WHITE = "#FFFFFF"
OFF_WHITE = "#F5F5F5"
LIGHT_GRAY = "#E0E0E0"
MEDIUM_GRAY = "#AAAAAA"
DARK_GRAY = "#888888"
TEXT_PRIMARY = "#333333"
TEXT_SECONDARY = "#666666"
TEXT_MUTED = "#999999"
SUCCESS = "#4CAF50"
ERROR = "#E53935"
WARNING = "#FF9800"
INFO = "#2196F3"
CYAN = "#00BCD4"
PURPLE = "#8B5CF6"


# ─── Status Colors ────────────────────────────────────────────────────────────

STATUS_COLORS = {
    "idle": MEDIUM_GRAY,
    "thinking": CYAN,
    "executing": GOLD,
    "error": ERROR,
    "offline": DARK_GRAY,
    "online": SUCCESS,
    "degraded": WARNING,
    "pending": MEDIUM_GRAY,
    "decomposing": INFO,
    "running": GOLD,
    "completed": SUCCESS,
    "failed": ERROR,
}


def get_status_color(status: str) -> str:
    return STATUS_COLORS.get(status, MEDIUM_GRAY)


# ─── KPI Card ─────────────────────────────────────────────────────────────────

class KPICard(ctk.CTkFrame):
    """A metric card showing a label, big number, and optional sub-text."""

    def __init__(self, parent, title: str, value: str, subtitle: str = "",
                 accent_color: str = GOLD, width: int = 170, **kwargs):
        super().__init__(parent, width=width, height=110, corner_radius=10,
                         fg_color=WHITE, border_width=1, border_color=LIGHT_GRAY, **kwargs)
        self.grid_propagate(False)
        self.columnconfigure(0, weight=1)

        # Color accent strip on top
        strip = ctk.CTkFrame(self, height=3, fg_color=accent_color, corner_radius=0)
        strip.grid(row=0, column=0, sticky="new", padx=0, pady=0)

        lbl_title = ctk.CTkLabel(self, text=title, text_color=TEXT_MUTED,
                                  font=ctk.CTkFont(size=11, weight="normal"))
        lbl_title.grid(row=1, column=0, padx=12, pady=(10, 0), sticky="nw")

        self._value_label = ctk.CTkLabel(self, text=value, text_color=accent_color,
                                          font=ctk.CTkFont(size=26, weight="bold"))
        self._value_label.grid(row=2, column=0, padx=12, pady=(2, 0), sticky="nw")

        if subtitle:
            lbl_sub = ctk.CTkLabel(self, text=subtitle, text_color=TEXT_MUTED,
                                    font=ctk.CTkFont(size=10))
            lbl_sub.grid(row=3, column=0, padx=12, pady=(0, 8), sticky="nw")

    def update_value(self, value: str):
        self._value_label.configure(text=value)


# ─── Status Badge ─────────────────────────────────────────────────────────────

class StatusBadge(ctk.CTkFrame):
    """Small colored badge showing a status label."""

    def __init__(self, parent, status: str, **kwargs):
        color = get_status_color(status)
        super().__init__(parent, corner_radius=10, fg_color=color, height=22, **kwargs)
        self.grid_propagate(False)
        lbl = ctk.CTkLabel(self, text=status.upper(), text_color=WHITE,
                            font=ctk.CTkFont(size=9, weight="bold"))
        lbl.pack(padx=10, pady=2)


# ─── Progress Bar ─────────────────────────────────────────────────────────────

class LabeledProgress(ctk.CTkFrame):
    """A labeled progress bar with percentage."""

    def __init__(self, parent, label: str, value: float = 0.0,
                 color: str = GOLD, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.columnconfigure(1, weight=1)

        self._label = ctk.CTkLabel(self, text=label, text_color=TEXT_SECONDARY,
                                    font=ctk.CTkFont(size=11), width=80, anchor="w")
        self._label.grid(row=0, column=0, padx=(0, 8), sticky="w")

        self._bar = ctk.CTkProgressBar(self, height=8, corner_radius=4,
                                        progress_color=color, fg_color=LIGHT_GRAY)
        self._bar.grid(row=0, column=1, sticky="ew")
        self._bar.set(value / 100.0 if value > 1 else value)

        self._pct = ctk.CTkLabel(self, text=f"{value:.0f}%", text_color=color,
                                  font=ctk.CTkFont(size=11, weight="bold"), width=45, anchor="e")
        self._pct.grid(row=0, column=2, padx=(8, 0), sticky="e")

    def update_value(self, value: float):
        self._bar.set(value / 100.0 if value > 1 else value)
        self._pct.configure(text=f"{value:.0f}%")


# ─── Event Row ────────────────────────────────────────────────────────────────

class EventRow(ctk.CTkFrame):
    """A single event entry for the event log."""

    SEVERITY_COLORS = {
        "info": TEXT_MUTED,
        "success": SUCCESS,
        "warning": WARNING,
        "error": ERROR,
    }
    SEVERITY_ICONS = {
        "info": "›",
        "success": "✓",
        "warning": "⚠",
        "error": "✗",
    }

    def __init__(self, parent, message: str, severity: str = "info", **kwargs):
        super().__init__(parent, fg_color="transparent", height=24, **kwargs)
        self.grid_propagate(False)
        self.columnconfigure(1, weight=1)

        color = self.SEVERITY_COLORS.get(severity, TEXT_MUTED)
        icon = self.SEVERITY_ICONS.get(severity, "›")

        lbl_icon = ctk.CTkLabel(self, text=icon, text_color=color,
                                 font=ctk.CTkFont(size=11, weight="bold"), width=16, anchor="w")
        lbl_icon.grid(row=0, column=0, padx=(4, 2), sticky="w")

        lbl_msg = ctk.CTkLabel(self, text=message, text_color=TEXT_SECONDARY,
                                font=ctk.CTkFont(size=11), anchor="w")
        lbl_msg.grid(row=0, column=1, padx=(0, 4), sticky="ew")


# ─── Agent List Item ──────────────────────────────────────────────────────────

class AgentListItem(ctk.CTkFrame):
    """A row displaying an agent's info and status."""

    def __init__(self, parent, agent: dict, on_click: Optional[Callable] = None, **kwargs):
        super().__init__(parent, corner_radius=8, fg_color=WHITE,
                         border_width=1, border_color=LIGHT_GRAY, height=56, **kwargs)
        self.grid_propagate(False)
        self.columnconfigure(2, weight=1)

        if on_click:
            self.bind("<Button-1>", lambda e: on_click(agent))
            self.configure(cursor="hand2")

        status = agent.get("status", "idle")
        color = get_status_color(status)

        # Icon
        icon_lbl = ctk.CTkLabel(self, text=agent.get("icon", "🤖"),
                                 font=ctk.CTkFont(size=18), width=36)
        icon_lbl.grid(row=0, column=0, rowspan=2, padx=(10, 4), sticky="w")

        # Name + Role
        name_lbl = ctk.CTkLabel(self, text=agent.get("name", "Agent"),
                                 text_color=TEXT_PRIMARY,
                                 font=ctk.CTkFont(size=13, weight="bold"), anchor="w")
        name_lbl.grid(row=0, column=1, columnspan=2, padx=(4, 10), pady=(8, 0), sticky="w")

        role_lbl = ctk.CTkLabel(self, text=agent.get("role", ""),
                                 text_color=TEXT_MUTED,
                                 font=ctk.CTkFont(size=10), anchor="w")
        role_lbl.grid(row=1, column=1, padx=(4, 10), pady=(0, 8), sticky="w")

        # Status dot
        status_frame = ctk.CTkFrame(self, width=10, height=10, corner_radius=5, fg_color=color)
        status_frame.grid(row=0, column=3, rowspan=2, padx=(0, 8), sticky="e")

        # CPU
        cpu_lbl = ctk.CTkLabel(self, text=f"{agent.get('cpu_percent', 0):.0f}%",
                                text_color=TEXT_MUTED,
                                font=ctk.CTkFont(size=10), width=40, anchor="e")
        cpu_lbl.grid(row=0, column=4, rowspan=2, padx=(0, 12), sticky="e")


# ─── Goal List Item ──────────────────────────────────────────────────────────

class GoalListItem(ctk.CTkFrame):
    """A row displaying a goal with progress."""

    def __init__(self, parent, goal: dict, **kwargs):
        super().__init__(parent, corner_radius=8, fg_color=WHITE,
                         border_width=1, border_color=LIGHT_GRAY, **kwargs)
        self.columnconfigure(0, weight=1)

        status = goal.get("status", "pending")
        color = get_status_color(status)
        progress = goal.get("progress", 0)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 0))
        top.columnconfigure(0, weight=1)

        title_lbl = ctk.CTkLabel(top, text=goal.get("title", "Goal"),
                                  text_color=TEXT_PRIMARY,
                                  font=ctk.CTkFont(size=13, weight="bold"), anchor="w")
        title_lbl.grid(row=0, column=0, sticky="w")

        badge = StatusBadge(top, status)
        badge.grid(row=0, column=1, sticky="e")

        if goal.get("description"):
            desc_lbl = ctk.CTkLabel(self, text=goal["description"][:100],
                                     text_color=TEXT_MUTED,
                                     font=ctk.CTkFont(size=10), anchor="w", wraplength=400)
            desc_lbl.grid(row=1, column=0, sticky="w", padx=12, pady=(2, 0))

        bar = ctk.CTkProgressBar(self, height=6, corner_radius=3,
                                  progress_color=color, fg_color=LIGHT_GRAY)
        bar.grid(row=2, column=0, sticky="ew", padx=12, pady=(6, 10))
        bar.set(progress / 100.0 if progress > 1 else progress)


# ─── Memory Entry Card ───────────────────────────────────────────────────────

class MemoryCard(ctk.CTkFrame):
    """A card displaying a memory entry."""

    def __init__(self, parent, entry: dict, **kwargs):
        super().__init__(parent, corner_radius=8, fg_color=WHITE,
                         border_width=1, border_color=LIGHT_GRAY, **kwargs)
        self.columnconfigure(0, weight=1)

        category = entry.get("category", "general")
        importance = entry.get("importance", 0.5)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 0))
        top.columnconfigure(0, weight=1)

        cat_lbl = ctk.CTkLabel(top, text=f"📁 {category}",
                                text_color=GOLD_DARK,
                                font=ctk.CTkFont(size=11, weight="bold"), anchor="w")
        cat_lbl.grid(row=0, column=0, sticky="w")

        imp_lbl = ctk.CTkLabel(top, text=f"Imp: {importance:.1f}",
                                text_color=TEXT_MUTED,
                                font=ctk.CTkFont(size=10), anchor="e")
        imp_lbl.grid(row=0, column=1, sticky="e")

        content = entry.get("content", "")
        if len(content) > 150:
            content = content[:150] + "..."
        content_lbl = ctk.CTkLabel(self, text=content, text_color=TEXT_SECONDARY,
                                    font=ctk.CTkFont(size=11), anchor="nw",
                                    wraplength=400, justify="left")
        content_lbl.grid(row=1, column=0, sticky="ew", padx=12, pady=(4, 10))


# ─── Section Header ──────────────────────────────────────────────────────────

class SectionHeader(ctk.CTkFrame):
    """A section header with title and optional action button."""

    def __init__(self, parent, title: str, button_text: str = "",
                 button_command: Optional[Callable] = None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.columnconfigure(0, weight=1)

        lbl = ctk.CTkLabel(self, text=title, text_color=TEXT_PRIMARY,
                            font=ctk.CTkFont(size=20, weight="bold"), anchor="w")
        lbl.grid(row=0, column=0, sticky="w")

        if button_text and button_command:
            btn = ctk.CTkButton(self, text=button_text, command=button_command,
                                 width=120, height=32, corner_radius=6,
                                 fg_color=GOLD, hover_color=GOLD_DARK,
                                 text_color=WHITE, font=ctk.CTkFont(size=12, weight="bold"))
            btn.grid(row=0, column=1, sticky="e")


# ─── Toast Notification ──────────────────────────────────────────────────────

class Toast:
    """Show a temporary notification overlay."""

    @staticmethod
    def show(parent, message: str, duration: int = 2000, color: str = SUCCESS):
        toast = ctk.CTkFrame(parent, fg_color=color, corner_radius=8, height=36)
        lbl = ctk.CTkLabel(toast, text=message, text_color=WHITE,
                            font=ctk.CTkFont(size=12, weight="bold"))
        lbl.pack(padx=16, pady=6)
        toast.place(relx=0.5, rely=0.95, anchor="center")
        parent.after(duration, toast.destroy)
