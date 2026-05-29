"""
initial_state.py — بيانات مثال الوظيفة
يمكن تعديل هذا الملف لتجربة حالات مختلفة
"""

from facts import NeedItem

# ── شبكة المعرض ─────────────────────────────────────────────
GRID = {"width": 5, "height": 5}

# ── المستودع ─────────────────────────────────────────────────
WAREHOUSE = {"x": 3, "y": 2}

# ── الروبوت: موقع البداية ────────────────────────────────────
ROBOT_START = {"x": 3, "y": 1}

# ── الأجنحة وبيانات الاحتياجات ──────────────────────────────
PAVILIONS = [
    {
        "id"         : "p1",
        "flower_type": "rose",
        "x": 4, "y": 2,
        "needs": [
            NeedItem("red",   2),
            NeedItem("pink",  1),
            NeedItem("white", 1),
        ],
    },
    {
        "id"         : "p2",
        "flower_type": "tulip",
        "x": 3, "y": 4,
        "needs": [
            NeedItem("red",    3),
            NeedItem("yellow", 1),
        ],
    },
    {
        "id"         : "p3",
        "flower_type": "orchid",
        "x": 5, "y": 4,
        "needs": [
            NeedItem("purple", 2),
            NeedItem("pink",   1),
        ],
    },
    {
        "id"         : "p4",
        "flower_type": "goliat",
        "x": 2, "y": 5,
        "needs": [
            NeedItem("gold",       2),
            NeedItem("light_pink", 2),
        ],
    },
]
