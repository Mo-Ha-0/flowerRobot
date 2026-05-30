"""
rules/goal_rules.py — قواعد الهدف والطباعة (المرحلة 5)

القواعد الثلاث:
  1. goal_rule       (salience=5) — يكتشف الحالة الهدف ويُخزّن الحل
  2. print_path_rule (salience=1) — يطبع مسار الحل خطوة بخطوة
  3. print_tree_rule (salience=1) — يطبع شجرة البحث كاملة

الحقائق الجديدة:
  GoalFound  — تُعلَن عند اكتشاف الحل
  SearchDone — تُعلَن من main.py بعد انتهاء البحث
"""

from collections import Counter

from experta import Fact, Field, Rule, MATCH, TEST

from facts  import SearchNode
from utils  import is_goal
from config import ACTION_ARROWS


# ══════════════════════════════════════════════════════════════
# الحقائق الجديدة
# ══════════════════════════════════════════════════════════════

class GoalFound(Fact):
    """
    تُعلَن حين يكتشف goal_rule الحالةَ الهدف.
    تُشغّل print_path_rule تلقائياً.
    """
    node_id = Field(str, mandatory=True)
    cost    = Field(int, mandatory=True)
    depth   = Field(int, mandatory=True)


class SearchDone(Fact):
    """
    تُعلَن من main.py بعد انتهاء engine.run().
    تُشغّل print_tree_rule تلقائياً.
    """
    total_nodes = Field(int, mandatory=True)


# ══════════════════════════════════════════════════════════════
# دوال مساعدة
# ══════════════════════════════════════════════════════════════

def reconstruct_path(all_nodes: list, goal_id: str) -> list:
    """
    تُعيد قائمة العقد من الجذر حتى الهدف.
    تسير عكسياً عبر parent_id حتى الجذر ثم تعكس القائمة.
    """
    node_map = {n["id"]: n for n in all_nodes}
    path, current = [], goal_id

    while current:
        node = node_map.get(current)
        if node is None:
            break
        path.append(node)
        parent = node.get("parent")
        if parent == current or parent is None:   # وصلنا للجذر
            break
        current = parent

    path.reverse()
    return path


def _action_key(action: str) -> str:
    """تُعيد اسم العملية الأساسي لاختيار رمز الطباعة."""
    if action.startswith("load"):
        return "load"
    if action.startswith("unload"):
        return "unload"
    return action.split("(")[0].split("@")[0]


def _format_bouquet_counts(counts: Counter) -> str:
    """تطبع الباقات مع الكمية حتى لا تضيع التكرارات المتطابقة."""
    parts = []
    for (flower_type, color), qty in sorted(counts.items()):
        parts.append(f"{flower_type}/{color}×{qty}")
    return "[" + ", ".join(parts) + "]"


def _format_step(node: dict, prev: dict | None) -> str:
    """تُنسّق خطوة واحدة في مسار الحل للطباعة."""
    arrow  = ACTION_ARROWS.get(_action_key(node["action"]), "?")
    action = node["action"]

    # ما تغيّر في الحمولة مقارنة بالخطوة السابقة
    detail = ""
    if prev:
        prev_bq = Counter(map(tuple, prev["bouquets"]))
        curr_bq = Counter(map(tuple, node["bouquets"]))
        loaded   = curr_bq - prev_bq
        unloaded = prev_bq - curr_bq
        if loaded:
            detail = f"← حمّل {_format_bouquet_counts(loaded)}"
        elif unloaded:
            detail = f"← سلّم {_format_bouquet_counts(unloaded)}"

    bq_str = (f"[{len(node['bouquets'])} باقات]"
              if node["bouquets"] else "فارغ")

    return (f"  {arrow} {action:35s}"
            f"  ({node['rx']},{node['ry']})"
            f"  g={node['cost']:2d}  {bq_str}"
            + (f"  {detail}" if detail else ""))


def print_solution(all_nodes: list, solution: dict):
    """تطبع مسار الحل الكامل بشكل منسّق."""
    sep = "═" * 65
    print(f"\n{sep}")
    print("  مسار الحل — تسلسل العمليات")
    print(sep)

    if solution is None:
        print("  لم يُعثر على حل.")
        print("  → استخدم A* في المرحلة 6 للحصول على الحل الأمثل.")
        print(sep)
        return

    path = solution["path"]
    print(f"  عدد الخطوات  : {len(path) - 1}")
    print(f"  التكلفة الكلية: {solution['cost']}")
    print(f"  العمق        : {solution['depth']}\n")

    prev = None
    for i, node in enumerate(path):
        print(_format_step(node, prev))
        prev = node

    # ملخص الأجنحة
    last = path[-1]
    print(f"\n  حالة الأجنحة في النهاية:")
    for p in last["pavilions"]:
        done_all = all(v[1] >= v[0] for v in p["needs"].values())
        icon = "✓" if done_all else "✗"
        details = {c: f"{v[1]}/{v[0]}" for c, v in p["needs"].items()}
        print(f"    {icon} {p['id']} ({p['flower_type']:6s}): {details}")
    print(sep)


def print_tree(all_nodes: list, max_show: int = 60):
    """تطبع شجرة البحث مرتّبةً بالعمق."""
    sep = "═" * 65
    print(f"\n{sep}")
    print("  شجرة البحث — جميع الحالات المولَّدة")
    print(sep)

    by_depth: dict[int, list] = {}
    for n in all_nodes:
        by_depth.setdefault(n["depth"], []).append(n)

    shown = 0
    for depth in sorted(by_depth):
        level = by_depth[depth]
        indent = "  " + "    " * depth
        print(f"\n  ── العمق {depth}  ({len(level)} عقدة) ──")
        for n in level:
            if shown >= max_show:
                print(f"\n  ... و {len(all_nodes)-shown} عقدة أخرى")
                print(sep)
                return
            arrow = ACTION_ARROWS.get(_action_key(n["action"]), "?")
            bq_str = (f"[{len(n['bouquets'])}]"
                      if n["bouquets"] else "∅")
            done = sum(1 for p in n["pavilions"]
                       if all(v[1] >= v[0]
                              for v in p["needs"].values()))
            total_pavs = len(n["pavilions"])
            print(f"{indent}{arrow} {n['action']:30s}"
                  f"  ({n['rx']},{n['ry']})"
                  f"  g={n['cost']:2d}  {bq_str}"
                  f"  ✓{done}/{total_pavs}")
            shown += 1

    print(f"\n{sep}")
    print(f"  إجمالي العقد : {len(all_nodes)}")
    print(sep)


# ══════════════════════════════════════════════════════════════
# الـ Mixin
# ══════════════════════════════════════════════════════════════

class GoalRulesMixin:
    """
    قواعد الهدف والطباعة — تُدمج في FlowerExhibitionKE.
    """

    # ════════════════════════════════════════════════════════
    # القاعدة 1: goal_rule  (salience=5)
    # ════════════════════════════════════════════════════════
    # تنطلق حين:
    #   - الروبوت فارغ (bouquets == [])
    #   - جميع الأجنحة استلمت احتياجاتها كاملة
    # الإجراء:
    #   - يُخزّن الحل في self.solution
    #   - يُعلن GoalFound لتشغيل print_path_rule
    #   - يوقف المحرك (halt)
    # ════════════════════════════════════════════════════════
    @Rule(
        SearchNode(
            node_id   = MATCH.nid,
            robot_x   = MATCH.rx,
            robot_y   = MATCH.ry,
            bouquets  = MATCH.bq,
            pavilions = MATCH.pavs,
            cost      = MATCH.cost,
            depth     = MATCH.depth,
        ),
        TEST(lambda bq, pavs: is_goal(list(bq), list(pavs))),
        salience = 5,
    )
    def goal_rule(self, nid, rx, ry, bq, pavs, cost, depth):
        # نُسجّل فقط أول حل — في DFS هو أعمق حل وليس بالضرورة الأمثل
        if self.solution is not None:
            return
        path = reconstruct_path(self.all_nodes, nid)
        self.solution = {
            "node_id": nid,
            "cost"   : cost,
            "depth"  : depth,
            "path"   : path,
        }
        # نُعلن GoalFound — print_path_rule (salience=1) ستطلق تالياً
        # لا halt() هنا: نترك print_path_rule تطلق أولاً ثم توقف
        self.declare(GoalFound(node_id=nid, cost=cost, depth=depth))

    # ════════════════════════════════════════════════════════
    # القاعدة 2: print_path_rule  (salience=1)
    # ════════════════════════════════════════════════════════
    # تنطلق حين يُعلَن GoalFound
    # تطبع مسار الحل كاملاً خطوة بخطوة
    # ════════════════════════════════════════════════════════
    @Rule(
        GoalFound(
            node_id = MATCH.nid,
            cost    = MATCH.cost,
            depth   = MATCH.depth,
        ),
        salience = 1,
    )
    def print_path_rule(self, nid, cost, depth):
        print(f"\n  ★ حالة الهدف وُجدت! تكلفة={cost}  عمق={depth}")
        print_solution(self.all_nodes, self.solution)
        # نوقف البحث بعد طباعة الحل
        self.halt()

    # ════════════════════════════════════════════════════════
    # القاعدة 3: print_tree_rule  (salience=1)
    # ════════════════════════════════════════════════════════
    # تنطلق حين تُعلَن SearchDone (من main.py بعد engine.run())
    # تطبع شجرة البحث كاملة
    # ════════════════════════════════════════════════════════
    @Rule(
        SearchDone(total_nodes=MATCH.total),
        salience = 1,
    )
    def print_tree_rule(self, total):
        print_tree(self.all_nodes)
        print(f"\n  ℹ  إجمالي الحالات المزارة : {len(self.visited)}")
        if self.violations_log:
            from collections import Counter
            by_rule = Counter(v["rule"] for v in self.violations_log)
            print(f"  ℹ  الانتهاكات المكتشفة  : {len(self.violations_log)}")
            for rule, cnt in by_rule.most_common():
                print(f"      • {rule}: {cnt}")
