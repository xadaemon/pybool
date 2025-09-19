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

BinOp = Enum(
    "BooleanOperation",
    [("AND", 0), ("OR", 1), ("XOR", 2), ("NAND", 3), ("NOR", 4)],
)


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
                return "0"
            case LV.BTrue:
                return "1"
            case LV.X:
                return "x"
            case LV.Z:
                return "z"

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

    def bin_op(self, other: "Logic", op: BinOp) -> "Logic":
        if not self._is_logic_val():
            raise ValueError("Cannot do operations on X and Z signals")
        match op:
            case BinOp.AND:
                return Logic(LV.BTrue if self and other else LV.BFalse)
            case BinOp.OR:
                return Logic(LV.BTrue if self or other else LV.BFalse)
            case BinOp.XOR:
                return Logic(
                    LV.BTrue
                    if (self or other) and (not (self and other))
                    else LV.BFalse
                )
            case BinOp.NAND:
                return Logic(LV.BTrue if not (self and other) else LV.BFalse)
            case BinOp.NOR:
                return Logic(LV.BTrue if not (self or other) else LV.BFalse)

    def negate(self):
        return Logic(LV.BFalse if self.val == LV.BTrue else LV.BTrue)

    @override
    def __str__(self) -> str:
        return self.__repr__()

    @staticmethod
    def n_of_val(n: int = 8, val: LogicValue = LV.BTrue) -> list["Logic"]:
        return [Logic(val) for _ in range(n)]


L_TRUE = Logic(LV.BTrue)
L_FALSE = Logic(LV.BFalse)

_logic_vec_default = Logic.n_of_val(8, LV.BFalse)


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

    def bin_op(self, other: "LogicVector", op: BinOp) -> "LogicVector":
        if other.width != self.width:
            other = other.extend(self.width)
        return LogicVector(
            self.width, [vs.bin_op(vo, op) for vs, vo in zip(self._vals, other._vals)]
        )

    def __or__(self, value: "LogicVector") -> "LogicVector":
        return self.bin_op(value, BinOp.OR)

    def __and__(self, value: "LogicVector") -> "LogicVector":
        return self.bin_op(value, BinOp.AND)

    def __xor__(self, value: "LogicVector") -> "LogicVector":
        return self.bin_op(value, BinOp.XOR)

    def __invert__(self) -> "LogicVector":
        return self.negate()

    def negate(self) -> "LogicVector":
        return LogicVector(self.width, [v.negate() for v in self._vals])

    def extend(self, by: int) -> "LogicVector":
        diff = by - self.width
        ext = Logic.n_of_val(diff, LV.BFalse)
        vals = copy(self._vals)
        vals.extend(ext)
        return LogicVector(self.width, vals)

    def sll(self, shift: int) -> "LogicVector":
        shifted = Logic.n_of_val(self.width, LV.BFalse)

        for bit in range(self.width):
            if bit + shift >= len(shifted):
                break
            shifted[bit + shift] = self._vals[bit]

        return LogicVector(self.width, shifted)

    # TODO: This implementation is definitely bad and needs a rework when I'm less sleepy
    def srl(self, shift: int) -> "LogicVector":
        shifted = Logic.n_of_val(self.width, LV.BFalse)
        rev = self._vals[::-1]

        for bit in range(self.width):
            if bit + shift >= len(shifted):
                break
            shifted[bit + shift] = rev[bit]

        return LogicVector(self.width, shifted[::-1])

    def __lshift__(self, by: int) -> "LogicVector":
        return self.sll(by)

    def __rshift__(self, by: int) -> "LogicVector":
        return self.srl(by)

    def __int__(self) -> int:
        ac: int = 0
        for bit in range(self.width):
            if self._vals[bit]:
                ac = ac + 2**bit
        return ac

    @staticmethod
    def from_int(v: int, width: int = 0) -> "LogicVector":
        bitwidth = width if width else v.bit_length()
        ret = Logic.n_of_val(bitwidth, LV.BFalse)
        for bit in range(bitwidth):
            mask = 1 << bit
            if (mask & v) != 0:
                ret[bit] = L_TRUE
        return LogicVector(bitwidth, ret)
