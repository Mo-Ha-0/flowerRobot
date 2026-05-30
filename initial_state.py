"""
initial_state.py — بيانات مثال الوظيفة
"""
from facts import NeedItem

GRID        = {"width": 5, "height": 5}
WAREHOUSE   = {"x": 3, "y": 2}
ROBOT_START = {"x": 3, "y": 1}

# ── المسألة الكاملة: 4 أجنحة ─────────────────────────────────
PAVILIONS = [
    {"id":"p1","flower_type":"rose",  "x":4,"y":2,
     "needs":[NeedItem("red",2),NeedItem("pink",1),NeedItem("white",1)]},
    {"id":"p2","flower_type":"tulip", "x":3,"y":4,
     "needs":[NeedItem("red",3),NeedItem("yellow",1)]},
    {"id":"p3","flower_type":"orchid","x":5,"y":4,
     "needs":[NeedItem("purple",2),NeedItem("pink",1)]},
    {"id":"p4","flower_type":"goliat","x":2,"y":5,
     "needs":[NeedItem("gold",2),NeedItem("light_pink",2)]},
]

# ── مسألة بسيطة للعرض: p1 مباشرة تحت المستودع ──────────────
# DFS يجد الحل في 4 خطوات مضمونة:
#   أسفل(مستودع) ← تحميل ← أسفل(p1) ← تفريغ
PAVILIONS_SIMPLE = [
    {"id":"p1","flower_type":"rose","x":3,"y":3,
     "needs":[NeedItem("red",2)]},
]