"""
engine.py — نظام الخبير الرئيسي
يجمع جميع الـ Mixins في كلاس واحد.
الاستراتيجية الافتراضية: DFS (Recency)
"""

from experta import KnowledgeEngine
from rules   import (MoveRulesMixin, LoadUnloadRulesMixin,
                     ConstraintRulesMixin, GoalRulesMixin)
from utils   import reset_counter


class FlowerExhibitionKE(
    MoveRulesMixin,
    LoadUnloadRulesMixin,
    ConstraintRulesMixin,
    GoalRulesMixin,
    KnowledgeEngine,
):
    """
    نظام الخبير — معرض الورود الذكي.

    السمات:
        visited    : set[str]   — هاشات الحالات المزارة
        all_nodes  : list[dict] — جميع العقد المولَّدة (للطباعة)
        solution   : dict|None  — أول حل يُعثر عليه
        max_depth  : int        — حد عمق البحث
        _node_log  : bool       — طباعة كل عقدة فور توليدها
    """

    def __init__(self, max_depth: int = 30, node_log: bool = False):
        super().__init__()
        self.visited        : set  = set()
        self.best_cost      : dict = {}
        self.all_nodes      : list = []
        self.solution       : dict = None
        self.max_depth      : int  = max_depth
        self._node_log      : bool = node_log
        self.violations_log : list = []   # سجل انتهاكات القيود (مرحلة 4)
        reset_counter()

    def _remember_state(self, state_key: str, cost: int) -> bool:
        """
        True إذا كانت الحالة جديدة أو وصلنا إليها بتكلفة أفضل.
        هذا يمنع مساراً عميقاً في DFS من حجب المسار الأقصر لنفس الحالة.
        """
        old_cost = self.best_cost.get(state_key)
        if old_cost is not None and old_cost <= cost:
            return False
        self.best_cost[state_key] = cost
        self.visited.add(state_key)
        return True

    # ── تسجيل العقد الجديدة ─────────────────────────────────
    def _log_node(self, node):
        """يُضاف إلى all_nodes ويطبع إذا كان node_log مفعَّلاً."""
        entry = {
            "id"       : node["node_id"],
            "parent"   : node["parent_id"],
            "action"   : node["action"],
            "rx"       : node["robot_x"],
            "ry"       : node["robot_y"],
            "cost"     : node["cost"],
            "depth"    : node["depth"],
            "bouquets" : list(node["bouquets"]),
            "pavilions": node["pavilions"],
        }
        self.all_nodes.append(entry)
        if self._node_log:
            from config import ACTION_ARROWS
            arrow = ACTION_ARROWS.get(node["action"], "?")
            print(f"  {arrow} [{node['node_id'][:40]}]"
                  f"  pos=({node['robot_x']},{node['robot_y']})"
                  f"  g={node['cost']}")
