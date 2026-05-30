"""
rules/load_unload_rules.py — قواعد التحميل والتفريغ (المرحلة 3)

قاعدة التحميل  (load_rule):
  الروبوت في المستودع + فارغ → يحمّل باقات وفق خيار أ أو خيار ب

قاعدة التفريغ  (unload_rule):
  الروبوت في جناح + يحمل باقات مناسبة → يسلّم ما يكفي

تكلفة كل عملية (تحميل أو تفريغ) = 1
"""

from collections import Counter, defaultdict
from experta import Rule, MATCH, TEST

from facts import SearchNode, WarehouseFact
from utils import state_hash, clone_pavilions, make_node_id


# ══════════════════════════════════════════════════════════════
# القسم 1 – دوال مساعدة للتحميل
# ══════════════════════════════════════════════════════════════

def _build_remaining(pavilions: list) -> tuple:
    """
    تبني خريطتَي الاحتياجات المتبقية:
      by_type  : {flower_type : {color : remaining_qty}}
      by_color : {color       : {flower_type : remaining_qty}}
    """
    by_type  = defaultdict(dict)
    by_color = defaultdict(dict)
    for pav in pavilions:
        ft = pav["flower_type"]
        for color, (req, done) in pav["needs"].items():
            rem = req - done
            if rem > 0:
                by_type[ft][color]  = by_type[ft].get(color, 0)  + rem
                by_color[color][ft] = by_color[color].get(ft, 0) + rem
    return dict(by_type), dict(by_color)


def is_valid_load(bouquets: list) -> bool:
    """
    يتحقق من أن قائمة الباقات صحيحة وفق القيود:
      - خيار أ: نفس اللون  (أنواع مختلفة مسموحة)
      - خيار ب: نفس النوع  (ألوان مختلفة مسموحة)
      - محظور : نوعان مختلفان + لونان مختلفان معاً
    """
    if not bouquets:
        return False
    types  = {bt for bt, bc in bouquets}
    colors = {bc for bt, bc in bouquets}
    return len(types) == 1 or len(colors) == 1


def generate_load_options(pavilions: list, max_load: int) -> list:
    """
    تولّد جميع خيارات التحميل الممكنة (لا تُعيد خيارات متطابقة).
    تُراعي:
      - خيار أ: نفس اللون، بأي كميات مطلوبة لا تتجاوز max_load
      - خيار ب: نفس النوع، بأي كميات مطلوبة لا تتجاوز max_load
      - الكمية القصوى: max_load
      - فائدة: كل باقة محمولة مطلوبة من جناح ما
    """
    by_type, by_color = _build_remaining(pavilions)
    seen    = set()
    options = []

    def _add(bq: list):
        if not bq:
            return
        if not is_valid_load(bq):          # ضمان القيد
            return
        key = tuple(sorted(bq))
        if key not in seen:
            seen.add(key)
            options.append(list(key))

    def _generate_group(items: list):
        """
        يولّد كل التركيبات غير الفارغة لعناصر مجموعة واحدة.
        items: [((flower_type, color), remaining_qty), ...]
        """
        ordered = sorted(items)

        def backtrack(index: int, current: list, total: int):
            if index == len(ordered):
                _add(current)
                return

            item, qty = ordered[index]
            max_count = min(qty, max_load - total)
            for count in range(max_count + 1):
                next_current = current + [item] * count
                backtrack(index + 1, next_current, total + count)

        backtrack(0, [], 0)

    # ── خيار ب: نفس النوع، ألوان مختلفة أو لون واحد ───────────
    for ft, color_needs in sorted(by_type.items()):
        items = [((ft, color), qty)
                 for color, qty in sorted(color_needs.items())]
        _generate_group(items)

    # ── خيار أ: نفس اللون، أنواع مختلفة أو نوع واحد ───────────
    for color, type_needs in sorted(by_color.items()):
        items = [((ft, color), qty)
                 for ft, qty in sorted(type_needs.items())]
        _generate_group(items)

    return options


# ══════════════════════════════════════════════════════════════
# القسم 2 – دوال مساعدة للتفريغ
# ══════════════════════════════════════════════════════════════

def find_pavilion_at(rx: int, ry: int, pavilions: list) -> dict | None:
    """تُعيد الجناح الموجود في الموقع (rx, ry) أو None."""
    for pav in pavilions:
        if pav["x"] == rx and pav["y"] == ry:
            return pav
    return None


def compute_unload(bouquets: list, pav: dict) -> tuple:
    """
    تحسب ما يمكن تسليمه لهذا الجناح في زيارة واحدة.

    الشرط لكل لون:
      - الروبوت يحمل باقات من نوع الجناح بهذا اللون
      - العدد المحمول >= ما تبقّى من الاحتياج

    عند التسليم: يُسلَّم بالضبط عدد الاحتياج المتبقي
                 (الفائض يبقى مع الروبوت)

    تُعيد:
      to_remove   : list[tuple] — الباقات التي تُزال من الروبوت
      updated_pav : dict المحدَّث، أو None إذا لا شيء قابل للتسليم
    """
    ft      = pav["flower_type"]
    carried = Counter(bc for bt, bc in bouquets if bt == ft)

    if not carried:
        return [], None

    to_remove    = []
    updated_needs = {c: [v[0], v[1]] for c, v in pav["needs"].items()}
    delivered_any = False

    for color, count in carried.items():
        if color not in updated_needs:
            continue
        req, done = updated_needs[color]
        remaining = req - done
        if remaining > 0 and count >= remaining:
            to_remove.extend([(ft, color)] * remaining)
            updated_needs[color][1] = req       # مكتمل
            delivered_any = True

    if not delivered_any:
        return [], None

    updated_pav = {
        "id"         : pav["id"],
        "flower_type": pav["flower_type"],
        "x"          : pav["x"],
        "y"          : pav["y"],
        "needs"      : updated_needs,
    }
    return to_remove, updated_pav


def can_unload_at(rx: int, ry: int, bouquets: list, pavilions: list) -> bool:
    """True إذا يمكن تفريغ شيء في الموقع (rx, ry)."""
    pav = find_pavilion_at(rx, ry, pavilions)
    if pav is None:
        return False
    to_remove, _ = compute_unload(bouquets, pav)
    return len(to_remove) > 0


def _apply_unload(bouquets: list, to_remove: list,
                  pavilions: list, updated_pav: dict) -> tuple:
    """
    تطبّق التفريغ وتُعيد:
      new_bouquets : الباقات المتبقية مع الروبوت
      new_pavilions: قائمة الأجنحة المحدَّثة
    """
    new_bq = list(bouquets)
    for item in to_remove:
        new_bq.remove(item)

    new_pavs = []
    for p in pavilions:
        if p["id"] == updated_pav["id"]:
            new_pavs.append(updated_pav)
        else:
            new_pavs.append({
                "id"         : p["id"],
                "flower_type": p["flower_type"],
                "x"          : p["x"],
                "y"          : p["y"],
                "needs"      : {c: [v[0], v[1]] for c, v in p["needs"].items()},
            })
    return new_bq, new_pavs


# ══════════════════════════════════════════════════════════════
# القسم 3 – الـ Mixin
# ══════════════════════════════════════════════════════════════

class LoadUnloadRulesMixin:
    """
    قواعد التحميل والتفريغ — تُدمج في FlowerExhibitionKE.
    """

    # ════════════════════════════════════════════════════════
    # قاعدة التحميل  (load_rule)
    # ════════════════════════════════════════════════════════
    #
    #  شروط الإطلاق:
    #    ① الروبوت في موقع المستودع  (rx==wx, ry==wy)
    #    ② الروبوت فارغ              (bouquets == [])
    #    ③ لا تزال هناك احتياجات    (any remaining need)
    #
    #  التأثير:
    #    لكل خيار تحميل صحيح → عقدة جديدة
    #    تكلفة += 1
    # ════════════════════════════════════════════════════════
    @Rule(
        SearchNode(
            node_id  = MATCH.nid,
            robot_x  = MATCH.rx,
            robot_y  = MATCH.ry,
            bouquets = MATCH.bq,
            pavilions= MATCH.pavs,
            max_load = MATCH.ml,
            cost     = MATCH.cost,
            depth    = MATCH.depth,
        ),
        WarehouseFact(x=MATCH.wx, y=MATCH.wy),
        TEST(lambda rx, ry, wx, wy: rx == wx and ry == wy),  # ① في المستودع
        TEST(lambda bq: len(bq) == 0),                        # ② فارغ
        TEST(lambda pavs: any(                                 # ③ احتياجات متبقية
            v[0] > v[1]
            for p in pavs
            for v in p["needs"].values()
        )),
    )
    def load_rule(self, nid, rx, ry, bq, pavs, ml, cost, depth, wx, wy):
        options = generate_load_options(pavs, ml)
        for opt_bq in options:
            new_cost = cost + 1
            if depth + 1 > self.max_depth:
                break
            h = state_hash(rx, ry, opt_bq, pavs)
            if not self._remember_state(h, new_cost):
                continue
            new_id   = make_node_id(nid, "load")
            # اسم العملية يوضّح ما تم تحميله
            types_loaded  = {bt for bt, bc in opt_bq}
            colors_loaded = {bc for bt, bc in opt_bq}
            if len(types_loaded) == 1:
                label = f"load_B({next(iter(types_loaded))})"     # خيار ب
            else:
                label = f"load_A({next(iter(colors_loaded))})"    # خيار أ
            new_node = SearchNode(
                node_id  = new_id,
                parent_id= nid,
                action   = label,
                robot_x  = rx,
                robot_y  = ry,
                bouquets = opt_bq,
                pavilions= clone_pavilions(pavs),
                max_load = ml,
                cost     = new_cost,
                depth    = depth + 1,
            )
            self.declare(new_node)
            self._log_node(new_node)

    # ════════════════════════════════════════════════════════
    # قاعدة التفريغ  (unload_rule)
    # ════════════════════════════════════════════════════════
    #
    #  شروط الإطلاق:
    #    ① الروبوت يحمل باقات        (bouquets != [])
    #    ② الروبوت في موقع جناح     (rx,ry matches pavilion)
    #    ③ يمكن تسليم شيء           (carried >= remaining for some color)
    #
    #  التأثير:
    #    تُسلَّم جميع الألوان القابلة للتسليم دفعة واحدة
    #    تكلفة += 1
    # ════════════════════════════════════════════════════════
    @Rule(
        SearchNode(
            node_id  = MATCH.nid,
            robot_x  = MATCH.rx,
            robot_y  = MATCH.ry,
            bouquets = MATCH.bq,
            pavilions= MATCH.pavs,
            max_load = MATCH.ml,
            cost     = MATCH.cost,
            depth    = MATCH.depth,
        ),
        TEST(lambda bq: len(bq) > 0),                               # ① يحمل
        TEST(lambda rx, ry, bq, pavs: can_unload_at(rx, ry, bq, pavs)),  # ②③
    )
    def unload_rule(self, nid, rx, ry, bq, pavs, ml, cost, depth):
        if depth + 1 > self.max_depth:
            return
        pav = find_pavilion_at(rx, ry, pavs)
        to_remove, updated_pav = compute_unload(bq, pav)
        new_bq, new_pavs = _apply_unload(bq, to_remove, pavs, updated_pav)
        h = state_hash(rx, ry, new_bq, new_pavs)
        new_cost = cost + 1
        if not self._remember_state(h, new_cost):
            return
        new_id = make_node_id(nid, "unload")
        colors_done = sorted({bc for _, bc in to_remove})
        action_label = f"unload@{pav['id']}[{','.join(colors_done)}]"
        new_node = SearchNode(
            node_id  = new_id,
            parent_id= nid,
            action   = action_label,
            robot_x  = rx,
            robot_y  = ry,
            bouquets = new_bq,
            pavilions= new_pavs,
            max_load = ml,
            cost     = new_cost,
            depth    = depth + 1,
        )
        self.declare(new_node)
        self._log_node(new_node)
