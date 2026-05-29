"""
utils/helpers.py — الدوال المساعدة المشتركة
  • state_hash       : تجزئة الحالة لمنع التكرار
  • clone_pavilions  : نسخ عميق للأجنحة
  • build_pavilions  : تحويل بيانات الحالة الابتدائية
  • compute_max_load : حساب الحمولة القصوى
  • make_node_id     : توليد معرّفات فريدة
  • is_goal          : التحقق من الحالة الهدف
"""

import copy
import hashlib
import json


# ══════════════════════════════════════════════════════════════
# تجزئة الحالة
# ══════════════════════════════════════════════════════════════

def state_hash(rx: int, ry: int,
               bouquets: list, pavilions: list) -> str:
    """
    تولّد معرّفاً مختصراً (MD5) للحالة الحالية.
    تعتمد على: موقع الروبوت + الباقات المحمولة + ما تبقّى لكل جناح.
    """
    bq_key = tuple(sorted(bouquets))
    pav_key = tuple(
        (p["id"],
         tuple(sorted(
             (c, v[0] - v[1])
             for c, v in p["needs"].items()
         )))
        for p in sorted(pavilions, key=lambda p: p["id"])
    )
    raw = json.dumps(
        {"rx": rx, "ry": ry, "bq": bq_key, "pav": pav_key},
        sort_keys=True, default=str
    )
    return hashlib.md5(raw.encode()).hexdigest()


# ══════════════════════════════════════════════════════════════
# بناء ونسخ بيانات الأجنحة
# ══════════════════════════════════════════════════════════════

def build_pavilions(pavilions_raw: list) -> list:
    """
    تحوّل قائمة الأجنحة الخام (من initial_state)
    إلى تمثيل dict قابل للنسخ والتجزئة.

    الصيغة الناتجة:
        [{"id": "p1", "flower_type": "rose", "x": 4, "y": 2,
          "needs": {"red": [2, 0], "pink": [1, 0]}}, ...]
    """
    result = []
    for pav in pavilions_raw:
        result.append({
            "id"         : pav["id"],
            "flower_type": pav["flower_type"],
            "x"          : pav["x"],
            "y"          : pav["y"],
            "needs"      : {
                ni.color: [ni.quantity, ni.delivered]
                for ni in pav["needs"]
            },
        })
    return result


def clone_pavilions(pavilions: list) -> list:
    """نسخة عميقة كاملة من قائمة الأجنحة."""
    return copy.deepcopy(pavilions)


# ══════════════════════════════════════════════════════════════
# حساب الحمولة القصوى
# ══════════════════════════════════════════════════════════════

def compute_max_load(pavilions_raw: list) -> int:
    """
    الحمولة القصوى = أكبر إجمالي باقات مطلوبة في جناح واحد.
    """
    return max(
        sum(ni.quantity for ni in pav["needs"])
        for pav in pavilions_raw
    )


# ══════════════════════════════════════════════════════════════
# توليد معرّفات العقد
# ══════════════════════════════════════════════════════════════

_counter = [0]

def reset_counter():
    _counter[0] = 0

def make_node_id(parent_id: str, action: str) -> str:
    """ينشئ معرّفاً فريداً للعقدة الجديدة."""
    _counter[0] += 1
    short_parent = parent_id.split("→")[-1][:15]
    return f"{short_parent}→{action}#{_counter[0]}"


# ══════════════════════════════════════════════════════════════
# شرط الإنهاء
# ══════════════════════════════════════════════════════════════

def is_goal(bouquets: list, pavilions: list) -> bool:
    """
    True إذا:
      - الروبوت لا يحمل أي باقات
      - جميع الأجنحة استلمت احتياجاتها كاملة
    """
    if bouquets:
        return False
    return all(
        v[1] >= v[0]
        for pav in pavilions
        for v in pav["needs"].values()
    )


# ══════════════════════════════════════════════════════════════
# دوال عرض مختصرة
# ══════════════════════════════════════════════════════════════

def pavilions_summary(pavilions: list) -> str:
    """ملخص مختصر لحالة الأجنحة (ما تبقّى من احتياجات)."""
    parts = []
    for p in pavilions:
        rem = {c: v[0]-v[1] for c, v in p["needs"].items() if v[0]-v[1] > 0}
        if rem:
            parts.append(f"{p['id']}:{rem}")
    return ", ".join(parts) if parts else "✓ مكتمل"


def bouquets_summary(bouquets: list) -> str:
    """ملخص مختصر للباقات المحمولة."""
    if not bouquets:
        return "فارغ"
    from collections import Counter
    c = Counter(bouquets)
    return ", ".join(f"{k[0]}/{k[1]}×{v}" for k, v in c.items())
