"""
rules/constraint_rules.py — قواعد منع انتهاك القيود (المرحلة 4)

القواعد الأربع (salience=10 > 0 لتنطلق قبل قواعد التوسيع):

  1. overload_violation      — تجاوز الحمولة القصوى
  2. invalid_load_violation  — تحميل نوعين مختلفين بلونين مختلفين
  3. wrong_type_violation    — الروبوت في جناح ويحمل نوعاً لا يناسبه
  4. out_of_bounds_violation — موقع الروبوت خارج حدود الشبكة

آلية العمل:
  • القواعد 1, 2, 4 تَسحب العقدة المنتهِكة من ذاكرة العمل (retract)
    لأن الحالة مستحيلة منطقياً ولا يجوز توسيعها.
  • القاعدة 3 تُسجّل التحذير فقط (لا سحب) لأن الروبوت قد يعبر
    الجناح دون تفريغ وهذا سلوك مسموح.
"""

from experta import Rule, MATCH, TEST, AS

from facts import SearchNode, GridFact


# ══════════════════════════════════════════════════════════════
# دوال مساعدة للتحقق من القيود
# ══════════════════════════════════════════════════════════════

def _bouquet_types(bouquets: list) -> set:
    """مجموعة أنواع الورود الموجودة في الحمولة."""
    return {bt for bt, bc in bouquets}


def _bouquet_colors(bouquets: list) -> set:
    """مجموعة الألوان الموجودة في الحمولة."""
    return {bc for bt, bc in bouquets}


def _is_overloaded(bouquets: list, max_load: int) -> bool:
    """True إذا تجاوز عدد الباقات الحد الأقصى."""
    return len(bouquets) > max_load


def _is_invalid_combination(bouquets: list) -> bool:
    """
    True إذا الحمولة تجمع نوعَين مختلفَين بلونَين مختلفَين —
    الحالة المحظورة صراحةً في الوظيفة.
    """
    if len(bouquets) < 2:
        return False                         # باقة واحدة أو فارغة → لا انتهاك
    types  = _bouquet_types(bouquets)
    colors = _bouquet_colors(bouquets)
    return len(types) > 1 and len(colors) > 1


def _wrong_type_at_pavilion(rx: int, ry: int,
                             bouquets: list, pavilions: list) -> bool:
    """
    True إذا:
      - الروبوت يقف في موقع جناح
      - الروبوت يحمل باقات
      - كل الباقات من نوع مختلف عن نوع هذا الجناح
      (الروبوت لن يستطيع تفريغ أي شيء هنا)
    """
    if not bouquets:
        return False
    pav = next((p for p in pavilions if p["x"] == rx and p["y"] == ry), None)
    if pav is None:
        return False                         # ليس في موقع جناح
    ft = pav["flower_type"]
    return all(bt != ft for bt, bc in bouquets)


def _is_out_of_bounds(rx: int, ry: int, gw: int, gh: int) -> bool:
    """True إذا موقع الروبوت خارج حدود الشبكة."""
    return not (1 <= rx <= gw and 1 <= ry <= gh)


# ══════════════════════════════════════════════════════════════
# الـ Mixin
# ══════════════════════════════════════════════════════════════

class ConstraintRulesMixin:
    """
    قواعد القيود — تُدمج في FlowerExhibitionKE.
    salience=10 يضمن انطلاقها قبل قواعد التوسيع (salience=0).
    """

    # ════════════════════════════════════════════════════════
    # القاعدة 1: overload_violation
    # الانتهاك: len(bouquets) > max_load
    # الإجراء : سحب العقدة + تسجيل الانتهاك
    # ════════════════════════════════════════════════════════
    @Rule(
        AS.node << SearchNode(
            node_id  = MATCH.nid,
            robot_x  = MATCH.rx,
            robot_y  = MATCH.ry,
            bouquets = MATCH.bq,
            max_load = MATCH.ml,
            cost     = MATCH.cost,
            depth    = MATCH.depth,
        ),
        TEST(lambda bq, ml: _is_overloaded(bq, ml)),
        salience = 10,
    )
    def overload_violation(self, node, nid, rx, ry, bq, ml, cost, depth):
        record = {
            "rule"    : "overload_violation",
            "node_id" : nid,
            "position": (rx, ry),
            "bouquets": list(bq),
            "max_load": ml,
            "carried" : len(bq),
            "cost"    : cost,
            "depth"   : depth,
            "detail"  : f"يحمل {len(bq)} باقة والحد هو {ml}",
        }
        self.violations_log.append(record)
        self.retract(node)         # سحب العقدة — لن تُوسَّع

    # ════════════════════════════════════════════════════════
    # القاعدة 2: invalid_load_violation
    # الانتهاك: نوعان مختلفان + لونان مختلفان في نفس الحمولة
    # الإجراء : سحب العقدة + تسجيل الانتهاك
    # ════════════════════════════════════════════════════════
    @Rule(
        AS.node << SearchNode(
            node_id  = MATCH.nid,
            robot_x  = MATCH.rx,
            robot_y  = MATCH.ry,
            bouquets = MATCH.bq,
            cost     = MATCH.cost,
            depth    = MATCH.depth,
        ),
        TEST(lambda bq: _is_invalid_combination(bq)),
        salience = 10,
    )
    def invalid_load_violation(self, node, nid, rx, ry, bq, cost, depth):
        types  = _bouquet_types(bq)
        colors = _bouquet_colors(bq)
        record = {
            "rule"    : "invalid_load_violation",
            "node_id" : nid,
            "position": (rx, ry),
            "bouquets": list(bq),
            "types"   : types,
            "colors"  : colors,
            "cost"    : cost,
            "depth"   : depth,
            "detail"  : (f"أنواع={types} و ألوان={colors} معاً — محظور"),
        }
        self.violations_log.append(record)
        self.retract(node)         # سحب العقدة — حالة مستحيلة

    # ════════════════════════════════════════════════════════
    # القاعدة 3: wrong_type_violation
    # الانتهاك: الروبوت في جناح ويحمل فقط نوعاً مختلفاً
    # الإجراء : تسجيل تحذير فقط (بدون سحب)
    #   — السبب: الروبوت قد يكون عابراً بالجناح في طريقه لمكان آخر.
    #     لكن التسجيل يُنبّه أن هذه الزيارة ستكون بلا فائدة.
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
        TEST(lambda bq: len(bq) > 0),
        TEST(lambda rx, ry, bq, pavs: _wrong_type_at_pavilion(rx, ry, bq, pavs)),
        salience = 10,
    )
    def wrong_type_violation(self, nid, rx, ry, bq, pavs, cost, depth):
        pav = next((p for p in pavs if p["x"] == rx and p["y"] == ry), None)
        pav_type   = pav["flower_type"] if pav else "?"
        carried    = _bouquet_types(bq)
        record = {
            "rule"       : "wrong_type_violation",
            "node_id"    : nid,
            "position"   : (rx, ry),
            "bouquets"   : list(bq),
            "pav_type"   : pav_type,
            "carried_types": carried,
            "cost"       : cost,
            "depth"      : depth,
            "detail"     : (
                f"الجناح يحتاج '{pav_type}' "
                f"لكن الروبوت يحمل {carried} فقط"
            ),
        }
        self.violations_log.append(record)
        # لا retract — الروبوت يستطيع المرور والتوجه لجناح آخر

    # ════════════════════════════════════════════════════════
    # القاعدة 4: out_of_bounds_violation
    # الانتهاك: موقع الروبوت خارج الشبكة
    # الإجراء : سحب العقدة + تسجيل الانتهاك
    # ════════════════════════════════════════════════════════
    @Rule(
        AS.node << SearchNode(
            node_id = MATCH.nid,
            robot_x = MATCH.rx,
            robot_y = MATCH.ry,
            cost    = MATCH.cost,
            depth   = MATCH.depth,
        ),
        GridFact(width=MATCH.gw, height=MATCH.gh),
        TEST(lambda rx, ry, gw, gh: _is_out_of_bounds(rx, ry, gw, gh)),
        salience = 10,
    )
    def out_of_bounds_violation(self, node, nid, rx, ry, gw, gh, cost, depth):
        record = {
            "rule"    : "out_of_bounds_violation",
            "node_id" : nid,
            "position": (rx, ry),
            "grid"    : (gw, gh),
            "cost"    : cost,
            "depth"   : depth,
            "detail"  : (
                f"موقع ({rx},{ry}) خارج الشبكة "
                f"{gw}×{gh}"
            ),
        }
        self.violations_log.append(record)
        self.retract(node)         # سحب العقدة — موقع مستحيل