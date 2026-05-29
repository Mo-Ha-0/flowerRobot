"""
config.py — إعدادات المشروع المركزية
معرض الورود الذكي | جامعة دمشق
"""

# ── حدود البحث ──────────────────────────────────────────────
MAX_DEPTH   : int = 30    # أقصى عمق لشجرة البحث
MAX_NODES   : int = 5000  # أقصى عدد عقد تُولَّد

# ── أنواع الورود وألوانها المتاحة ───────────────────────────
FLOWER_COLORS: dict[str, list[str]] = {
    "rose"  : ["red", "pink", "white", "yellow", "crimson"],
    "tulip" : ["red", "yellow", "purple", "orange",
               "green", "mauve", "violet"],
    "orchid": ["purple", "white", "pink", "magenta"],
    "goliat": ["gold", "light_pink", "yellow"],
}

# ── رموز طباعة الاتجاهات ────────────────────────────────────
ACTION_ARROWS: dict[str, str] = {
    "move_right": "→",
    "move_left" : "←",
    "move_up"   : "↑",
    "move_down" : "↓",
    "load"      : "▲",
    "unload"    : "▼",
    "start"     : "★",
}
