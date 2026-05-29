"""
rules/move_rules.py — قواعد الحركة (المرحلة 2)
  move_right | move_left | move_up | move_down
تكلفة كل خطوة = 1
"""

from experta import Rule, MATCH
from facts import SearchNode, GridFact
from utils import state_hash, clone_pavilions, make_node_id


class MoveRulesMixin:
    """
    Mixin يُضاف إلى FlowerExhibitionKE.
    يحتوي على القواعد الأربع للحركة.
    """

    # ── دالة داخلية مشتركة ──────────────────────────────────
    def _try_move(self, node_id, rx, ry, new_rx, new_ry,
                  bq, pavs, ml, cost, depth, action, gw, gh):
        """
        تتحقق من صحة الحركة وتُعلن العقدة الجديدة إن لم تُزَر.
        القيود:
          1) الموقع الجديد داخل حدود الشبكة
          2) الحالة لم تُزَر مسبقاً
          3) العمق لم يتجاوز الحد الأقصى
        """
        # قيد الحدود
        if not (1 <= new_rx <= gw and 1 <= new_ry <= gh):
            return

        # قيد التكرار
        h = state_hash(new_rx, new_ry, bq, pavs)
        if h in self.visited:
            return

        # قيد العمق
        if depth + 1 > self.max_depth:
            return

        # ── إعلان العقدة الجديدة ────────────────────────────
        self.visited.add(h)
        new_id   = make_node_id(node_id, action)
        new_pavs = clone_pavilions(pavs)

        new_node = SearchNode(
            node_id   = new_id,
            parent_id = node_id,
            action    = action,
            robot_x   = new_rx,
            robot_y   = new_ry,
            bouquets  = list(bq),
            pavilions = new_pavs,
            max_load  = ml,
            cost      = cost + 1,
            depth     = depth + 1,
        )
        self.declare(new_node)
        self._log_node(new_node)

    # ════════════════════════════════════════════════════════
    # القاعدة 1: move_right  →  X += 1
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
        GridFact(width=MATCH.gw, height=MATCH.gh),
    )
    def move_right(self, nid, rx, ry, bq, pavs, ml, cost, depth, gw, gh):
        self._try_move(nid, rx, ry, rx+1, ry,
                       bq, pavs, ml, cost, depth,
                       "move_right", gw, gh)

    # ════════════════════════════════════════════════════════
    # القاعدة 2: move_left  →  X -= 1
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
        GridFact(width=MATCH.gw, height=MATCH.gh),
    )
    def move_left(self, nid, rx, ry, bq, pavs, ml, cost, depth, gw, gh):
        self._try_move(nid, rx, ry, rx-1, ry,
                       bq, pavs, ml, cost, depth,
                       "move_left", gw, gh)

    # ════════════════════════════════════════════════════════
    # القاعدة 3: move_up  →  Y -= 1  (الأعلى = Y أصغر)
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
        GridFact(width=MATCH.gw, height=MATCH.gh),
    )
    def move_up(self, nid, rx, ry, bq, pavs, ml, cost, depth, gw, gh):
        self._try_move(nid, rx, ry, rx, ry-1,
                       bq, pavs, ml, cost, depth,
                       "move_up", gw, gh)

    # ════════════════════════════════════════════════════════
    # القاعدة 4: move_down  →  Y += 1
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
        GridFact(width=MATCH.gw, height=MATCH.gh),
    )
    def move_down(self, nid, rx, ry, bq, pavs, ml, cost, depth, gw, gh):
        self._try_move(nid, rx, ry, rx, ry+1,
                       bq, pavs, ml, cost, depth,
                       "move_down", gw, gh)
