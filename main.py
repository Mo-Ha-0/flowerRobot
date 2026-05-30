"""
main.py — نقطة التشغيل الرئيسية
معرض الورود الذكي | جامعة دمشق

الاستخدام:
    python main.py              ← المسألة الكاملة (4 أجنحة، يحتاج A*)
    python main.py --simple     ← مسألة بسيطة (1 جناح) تُظهر المراحل 2-5
    python main.py --tree       ← مع طباعة شجرة البحث (print_tree_rule)
    python main.py --depth N    ← تحديد حد العمق
    python main.py --log        ← طباعة كل عقدة فور توليدها
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import argparse
from facts         import GridFact, WarehouseFact, SearchNode
from initial_state import GRID, WAREHOUSE, ROBOT_START, PAVILIONS, PAVILIONS_SIMPLE
from engine        import FlowerExhibitionKE
from rules.goal_rules import SearchDone
from utils         import (build_pavilions, compute_max_load,
                            state_hash, reset_counter)
from config        import MAX_DEPTH


def build_engine(max_depth=MAX_DEPTH, node_log=False,
                 simple=False) -> FlowerExhibitionKE:
    """تُنشئ المحرك وتُعلن الحالة الابتدائية."""
    pavs_raw  = PAVILIONS_SIMPLE if simple else PAVILIONS
    pavilions = build_pavilions(pavs_raw)
    max_load  = compute_max_load(pavs_raw)
    rx, ry    = ROBOT_START["x"], ROBOT_START["y"]

    engine = FlowerExhibitionKE(max_depth=max_depth, node_log=node_log)
    engine.reset()
    engine.declare(GridFact(width=GRID["width"], height=GRID["height"]))
    engine.declare(WarehouseFact(x=WAREHOUSE["x"], y=WAREHOUSE["y"]))

    root_hash = state_hash(rx, ry, [], pavilions)
    engine._remember_state(root_hash, 0)
    root = SearchNode(
        node_id="root", parent_id="root", action="start",
        robot_x=rx, robot_y=ry, bouquets=[], pavilions=pavilions,
        max_load=max_load, cost=0, depth=0,
    )
    engine.declare(root)
    engine._log_node(root)
    return engine


def main():
    parser = argparse.ArgumentParser(
        description="معرض الورود الذكي – روبوت توزيع الباقات"
    )
    parser.add_argument("--depth",  type=int, default=None)
    parser.add_argument("--log",    action="store_true")
    parser.add_argument("--simple", action="store_true")
    parser.add_argument("--tree",   action="store_true")
    args = parser.parse_args()

    if args.depth is None:
        args.depth = 8 if args.simple else 30

    mode  = "بسيطة — 1 جناح" if args.simple else "كاملة — 4 أجنحة"
    npavs = 1 if args.simple else 4

    print("╔" + "═"*60 + "╗")
    print("║      معرض الورود الذكي – روبوت توزيع الباقات          ║")
    print("╠" + "═"*60 + "╣")
    print(f"║  المسألة : {mode:<49s}║")
    print(f"║  البحث   : DFS (Recency)  |  حد العمق = {args.depth:<18d}║")
    print("╚" + "═"*60 + "╝\n")

    # ── البحث (القواعد 2+3+4 + goal_rule + print_path_rule) ─
    print("  ▶ مرحلة البحث...")
    engine = build_engine(max_depth=args.depth,
                          node_log=args.log,
                          simple=args.simple)
    engine.run()   # goal_rule + print_path_rule تطلقان تلقائياً

    # ── ملخص ─────────────────────────────────────────────────
    sep = "─"*62
    print(f"\n{sep}")
    print(f"  العقد المولَّدة  : {len(engine.all_nodes)}")
    print(f"  الحالات المزارة : {len(engine.visited)}")
    print(f"  الانتهاكات      : {len(engine.violations_log)}")
    if engine.solution:
        print(f"  الحل ✓          : تكلفة = {engine.solution['cost']}"
              f"  |  خطوات = {len(engine.solution['path'])-1}")
    else:
        print(f"  الحل ✗          : لم يُعثر عند عمق {args.depth}")
        print(f"    → المسألة الكاملة تحتاج A* (المرحلة 6)")
    print(sep)

    # ── شجرة البحث (print_tree_rule) ─────────────────────────
    if args.tree:
        print("\n  ▶ طباعة شجرة البحث (قاعدة print_tree_rule)...")
        engine.declare(SearchDone(total_nodes=len(engine.all_nodes)))
        engine.run()


if __name__ == "__main__":
    main()
