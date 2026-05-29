"""
main.py — نقطة التشغيل الرئيسية
معرض الورود الذكي | جامعة دمشق

الاستخدام:
    python main.py [--depth N] [--log]
"""

import sys
import argparse

from experta    import KnowledgeEngine
from facts      import GridFact, WarehouseFact, SearchNode
from initial_state import GRID, WAREHOUSE, ROBOT_START, PAVILIONS
from engine     import FlowerExhibitionKE
from utils      import (build_pavilions, compute_max_load,
                         state_hash, make_node_id,
                         print_search_tree, print_stats)
from config     import MAX_DEPTH


# ══════════════════════════════════════════════════════════════
# بناء وتهيئة المحرك
# ══════════════════════════════════════════════════════════════

def build_engine(max_depth: int = MAX_DEPTH,
                 node_log:  bool = False) -> FlowerExhibitionKE:
    """
    تُنشئ المحرك، تُعلن الحقائق الثابتة والعقدة الجذر.
    """
    pavilions = build_pavilions(PAVILIONS)
    max_load  = compute_max_load(PAVILIONS)
    rx, ry    = ROBOT_START["x"], ROBOT_START["y"]

    engine = FlowerExhibitionKE(max_depth=max_depth, node_log=node_log)
    engine.reset()

    # ── حقائق البيئة ──────────────────────────────────────
    engine.declare(GridFact(width=GRID["width"], height=GRID["height"]))
    engine.declare(WarehouseFact(x=WAREHOUSE["x"], y=WAREHOUSE["y"]))

    # ── العقدة الجذر ──────────────────────────────────────
    root_bq   = []
    root_hash = state_hash(rx, ry, root_bq, pavilions)
    engine.visited.add(root_hash)

    root = SearchNode(
        node_id   = "root",
        parent_id = "root",
        action    = "start",
        robot_x   = rx,
        robot_y   = ry,
        bouquets  = root_bq,
        pavilions = pavilions,
        max_load  = max_load,
        cost      = 0,
        depth     = 0,
    )
    engine.declare(root)
    engine._log_node(root)

    return engine


# ══════════════════════════════════════════════════════════════
# نقطة الدخول
# ══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="معرض الورود الذكي – روبوت توزيع الباقات"
    )
    parser.add_argument("--depth", type=int, default=5,
                        help="حد عمق البحث (الافتراضي: 5)")
    parser.add_argument("--log", action="store_true",
                        help="اطبع كل عقدة فور توليدها")
    args = parser.parse_args()

    print("╔" + "═" * 58 + "╗")
    print("║     معرض الورود الذكي – روبوت توزيع الباقات          ║")
    print("║     جامعة دمشق | نظم قواعد المعرفة                    ║")
    print("╠" + "═" * 58 + "╣")
    print(f"║  استراتيجية البحث : DFS (Recency)                     ║")
    print(f"║  حد العمق         : {args.depth:<5}                          ║")
    print(f"║  الشبكة           : {GRID['width']}×{GRID['height']}                            ║")
    print(f"║  الروبوت          : ({ROBOT_START['x']},{ROBOT_START['y']})                          ║")
    print(f"║  المستودع         : ({WAREHOUSE['x']},{WAREHOUSE['y']})                          ║")
    print("╚" + "═" * 58 + "╝")

    # ── بناء المحرك وتشغيله ───────────────────────────────
    engine = build_engine(max_depth=args.depth, node_log=args.log)

    print(f"\n  ▶ تشغيل محرك الاستدلال...\n")
    engine.run()

    # ── إحصائيات ──────────────────────────────────────────
    print_stats(engine)

    # ── شجرة البحث ────────────────────────────────────────
    print_search_tree(engine.all_nodes, max_show=60)

    # ── الحل (إن وُجد) ────────────────────────────────────
    if engine.solution:
        from utils import print_solution_path
        print_solution_path(
            engine.solution["path"],
            engine.solution["cost"]
        )
    else:
        print("\n  ℹ  لم يُعثر على حل بعد إكمال المراحل 3 و 4 و 5.")


if __name__ == "__main__":
    main()
