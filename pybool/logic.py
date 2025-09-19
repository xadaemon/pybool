from copy import copy
from enum import Enum
from typing import override

# Valid logic values
class LogicValue(Enum):
    BFalse = 0
    BTrue = 1
    X = 2
    Z = 3

    @staticmethod
    def from_bool(v: bool) -> "LogicValue":
        return LogicValue.BTrue if v else LogicValue.BFalse

LV = LogicValue

BoolOp = Enum("BooleanOperation", [
    ("AND", 0),
    ("OR", 1),
    ("XOR", 2),
    ("NAND", 3),
    ("NOR", 4),
    ("NOT", 5)
])

class Logic:
    val: LogicValue = LogicValue.X
    def __init__(self, val: LogicValue | bool = LV.X) -> None:
        if isinstance(val, bool):
            val = LogicValue.from_bool(val)
        self.val = val

    @override
    def __repr__(self) -> str:
        match self.val:
            case LV.BFalse:
                return '0'
            case LV.BTrue:
                return '1'
            case LV.X:
                return 'x'
            case LV.Z:
                return 'z'

    def _is_logic_val(self) -> bool:
        return not self.val in [LV.X, LV.Z]

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Logic):
            raise ValueError("Cannot compare Logic and non Logic object")
        return other.val == self.val

    def __bool__(self) -> bool:
        if not self._is_logic_val():
            raise ValueError("X and Z state cannot be converted to boolean")
        return True if self.val == LV.BTrue else False

    def bool_op(self, other: "Logic", op: BoolOp) -> "Logic":
        if not self._is_logic_val():
            raise ValueError("Cannot do operations on X and Z signals")
        match op:
            case BoolOp.AND:
                return Logic(LV.BTrue if self and other else LV.BFalse)
            case BoolOp.OR:
                return Logic(LV.BTrue if self or other else LV.BFalse)
            case BoolOp.XOR:
                return Logic(LV.BTrue if (self or other) and (not (self and other)) else LV.BFalse)
            case BoolOp.NAND:
                return Logic(LV.BTrue if not (self and other) else LV.BFalse)
            case BoolOp.NOR:
                return Logic(LV.BTrue if not (self or other) else LV.BFalse)
            case BoolOp.NOT:
                return Logic(LV.BFalse if self.val == LV.BTrue else LV.BTrue)

    @override
    def __str__(self) -> str:
        return self.__repr__()

    @staticmethod
    def n_of_val(n: int = 8, val: LogicValue = LV.BTrue) -> list["Logic"]:
        return [Logic(val) for _ in range(n)]


L_TRUE = Logic(LV.BTrue)
L_FALSE = Logic(LV.BFalse)

_logic_vec_default = Logic.n_of_val(8)

class LogicVector:
    width: int = 0
    _vals: list[Logic] = []

    def __init__(self, width: int = 8, vals: list[Logic] = _logic_vec_default) -> None:
        self.width = width
        self._vals = copy(vals)

    @override
    def __repr__(self) -> str:
        vs = [str(v) for v in self._vals]
        return " ".join(vs[::-1])

    def __getitem__(self, item: int) -> Logic:
        return self._vals[item]

    def __setitem__(self, item: int, val: Logic | LogicValue | bool) -> None:
        if isinstance(val, LogicValue):
            val = Logic(val)
        elif isinstance(val, bool):
            val = Logic(val)
        self._vals[item] = val

    def bool_op(self, other: "LogicVector", op: BoolOp) -> "LogicVector":
        return LogicVector(self.width, [vs.bool_op(vo, op) for vs, vo in zip(self._vals, other._vals)])

