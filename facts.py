"""
facts.py — تعريف جميع الحقائق (Facts)
المرحلة 1: تمثيل الحالة
"""

from experta import Fact, Field


# ══════════════════════════════════════════════════════════════
# حقائق بيئة المعرض
# ══════════════════════════════════════════════════════════════

class GridFact(Fact):
    """أبعاد شبكة المعرض."""
    width  = Field(int, mandatory=True)   # عدد الأعمدة (X)
    height = Field(int, mandatory=True)   # عدد الصفوف  (Y)


class WarehouseFact(Fact):
    """موقع المستودع المركزي."""
    x = Field(int, mandatory=True)
    y = Field(int, mandatory=True)


# ══════════════════════════════════════════════════════════════
# كائنات مساعدة (غير Fact — تُخزَّن داخل الحقائق)
# ══════════════════════════════════════════════════════════════

class BouquetItem:
    """
    باقة فردية يحملها الروبوت.
      flower_type : نوع الورد  (rose / tulip / orchid / goliat)
      color       : اللون
    """
    __slots__ = ("flower_type", "color")

    def __init__(self, flower_type: str, color: str):
        self.flower_type = flower_type
        self.color       = color

    def __repr__(self):
        return f"Bouquet({self.flower_type},{self.color})"

    def __eq__(self, other):
        return (isinstance(other, BouquetItem) and
                self.flower_type == other.flower_type and
                self.color == other.color)

    def __hash__(self):
        return hash((self.flower_type, self.color))

    def to_tuple(self) -> tuple:
        return (self.flower_type, self.color)


class NeedItem:
    """
    احتياج لون محدد داخل الجناح.
      color     : اللون المطلوب
      quantity  : الكمية المطلوبة
      delivered : الكمية المسلَّمة حتى الآن
    """
    __slots__ = ("color", "quantity", "delivered")

    def __init__(self, color: str, quantity: int, delivered: int = 0):
        self.color     = color
        self.quantity  = quantity
        self.delivered = delivered

    @property
    def remaining(self) -> int:
        return self.quantity - self.delivered

    @property
    def fulfilled(self) -> bool:
        return self.delivered >= self.quantity

    def __repr__(self):
        return (f"NeedItem({self.color},"
                f"req={self.quantity},done={self.delivered})")


# ══════════════════════════════════════════════════════════════
# حقائق الكيانات المتحركة
# ══════════════════════════════════════════════════════════════

class PavilionFact(Fact):
    """
    جناح في المعرض (للحالة الابتدائية فقط).
      pavilion_id : معرّف فريد
      flower_type : نوع الورد المخصص
      x, y        : الموقع
      needs       : list[NeedItem]
    """
    pavilion_id = Field(str,  mandatory=True)
    flower_type = Field(str,  mandatory=True)
    x           = Field(int,  mandatory=True)
    y           = Field(int,  mandatory=True)
    needs       = Field(list, mandatory=True)


class SearchNode(Fact):
    """
    عقدة في شجرة البحث — الحالة الكاملة للنظام.

    بنية كل عنصر في pavilions (list[dict]):
    {
      "id"          : "p1",
      "flower_type" : "rose",
      "x"  : 4, "y": 2,
      "needs": { "red": [qty_required, qty_delivered], ... }
    }

    بنية كل عنصر في bouquets (list[tuple]):
      ("rose", "red")
    """
    node_id   = Field(str,  mandatory=True)   # معرّف فريد
    parent_id = Field(str,  mandatory=True)   # معرّف العقدة الأم
    action    = Field(str,  mandatory=True)   # العملية المنفَّذة
    robot_x   = Field(int,  mandatory=True)
    robot_y   = Field(int,  mandatory=True)
    bouquets  = Field(list, mandatory=True)   # list[tuple]
    pavilions = Field(list, mandatory=True)   # list[dict]
    max_load  = Field(int,  mandatory=True)
    cost      = Field(int,  mandatory=True)   # g(n)
    depth     = Field(int,  mandatory=True)
