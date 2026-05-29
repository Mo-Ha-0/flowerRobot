"""
utils/printer.py — طباعة شجرة البحث ومسار الحل
"""

from config import ACTION_ARROWS


def print_search_tree(nodes: list, max_show: int = 50):
    """
    تطبع شجرة البحث مرتّبةً بالعمق.
    """
    sep = "═" * 62
    print(f"\n{sep}")
    print("  شجرة البحث — جميع الحالات المولَّدة")
    print(sep)

    by_depth: dict[int, list] = {}
    for n in nodes:
        by_depth.setdefault(n["depth"], []).append(n)

    shown = 0
    for depth in sorted(by_depth):
        level = by_depth[depth]
        indent = "  " + "    " * depth
        print(f"\n  ── العمق {depth}  ({len(level)} عقدة) ──")
        for n in level:
            if shown >= max_show:
                print(f"\n  ... و {len(nodes) - shown} عقدة أخرى لم تُعرض")
                print(sep)
                return
            arrow = ACTION_ARROWS.get(n["action"], "?")
            bq_str = (f"[{len(n['bouquets'])} باقات]"
                      if n["bouquets"] else "فارغ")
            print(
                f"{indent}{arrow} {n['action']:12s}"
                f"  pos=({n['rx']},{n['ry']})"
                f"  g={n['cost']}  {bq_str}"
            )
            shown += 1

    print(f"\n{sep}")
    print(f"  إجمالي العقد : {len(nodes)}")
    print(sep)


def print_solution_path(path: list, total_cost: int):
    """
    تطبع مسار الحل خطوة بخطوة.
    path : list[dict] — كل عنصر { action, rx, ry, cost, detail }
    """
    sep = "═" * 62
    print(f"\n{sep}")
    print("  مسار الحل الأمثل")
    print(sep)

    if not path:
        print("  لم يُعثر على حل.")
        print(sep)
        return

    for i, step in enumerate(path):
        arrow  = ACTION_ARROWS.get(step.get("action", "?"), "?")
        detail = step.get("detail", "")
        print(
            f"  {i:>3}. {arrow} {step['action']:12s}"
            f"  pos=({step['rx']},{step['ry']})"
            f"  g={step['cost']}"
            + (f"  [{detail}]" if detail else "")
        )

    print(f"\n  التكلفة الإجمالية : {total_cost}")
    print(sep)


def print_stats(engine):
    """
    تطبع إحصائيات البحث.
    """
    sep = "─" * 62
    nodes = engine.all_nodes
    by_depth: dict[int, int] = {}
    for n in nodes:
        by_depth[n["depth"]] = by_depth.get(n["depth"], 0) + 1

    print(f"\n{sep}")
    print("  إحصائيات البحث")
    print(sep)
    print(f"  العقد المولَّدة   : {len(nodes)}")
    print(f"  الحالات المزارة   : {len(engine.visited)}")
    print(f"  أقصى عمق بلغه    : {max(by_depth, default=0)}")
    if engine.solution:
        print(f"  تكلفة الحل       : {engine.solution['cost']}")
        print(f"  طول المسار       : {len(engine.solution['path'])} خطوة")
    else:
        print("  الحل             : لم يُعثر عليه")
    print(f"\n  توزيع العقد على الأعماق:")
    for d in sorted(by_depth):
        bar = "█" * min(by_depth[d], 35)
        print(f"    عمق {d:2d}: {by_depth[d]:4d}  {bar}")
    print(sep)
