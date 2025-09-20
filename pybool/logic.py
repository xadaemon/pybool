from copy import copy
from enum import Enum
from typing import override

BinOp = Enum(
    "BooleanOperation",
    [("AND", 0), ("OR", 1), ("XOR", 2), ("NAND", 3), ("NOR", 4)],
)


# Valid logic values
class Logic(Enum):
    false = 0
    true = 1
    x = 2
    z = 3

    @staticmethod
    def from_bool(v: bool) -> "Logic":
        return Logic.true if v else Logic.false

    @override
    def __repr__(self) -> str:
        match self:
            case Logic.false:
                return "0"
            case Logic.true:
                return "1"
            case Logic.x:
                return "x"
            case Logic.z:
                return "z"

    def _is_logic_val(self) -> bool:
        return not self in [Logic.x, Logic.z]

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Logic):
            raise ValueError("Cannot compare Logic and non Logic object")
        return self.value == other.value

    def __bool__(self) -> bool:
        if not self._is_logic_val():
            raise ValueError("X and Z state cannot be converted to boolean")
        return True if self == Logic.true else False

    def bin_op(self, other: "Logic", op: BinOp) -> "Logic":
        if not self._is_logic_val():
            raise ValueError("Cannot do operations on X and Z signals")
        match op:
            case BinOp.AND:
                return Logic(Logic.true if self and other else Logic.false)
            case BinOp.OR:
                return Logic(Logic.true if self or other else Logic.false)
            case BinOp.XOR:
                return Logic(
                    Logic.true
                    if (self or other) and (not (self and other))
                    else Logic.false
                )
            case BinOp.NAND:
                return Logic(Logic.true if not (self and other) else Logic.false)
            case BinOp.NOR:
                return Logic(Logic.true if not (self or other) else Logic.false)

    def negate(self):
        return Logic(Logic.false if self == Logic.true else Logic.true)

    def __or__(self, value: "Logic") -> "Logic":
        return self.bin_op(value, BinOp.OR)

    def __and__(self, value: "Logic") -> "Logic":
        return self.bin_op(value, BinOp.AND)

    def __xor__(self, value: "Logic") -> "Logic":
        return self.bin_op(value, BinOp.XOR)

    def __invert__(self) -> "Logic":
        return self.negate()

    @override
    def __str__(self) -> str:
        return self.__repr__()

    @staticmethod
    def n_of_val(n: int, val: "Logic") -> list["Logic"]:
        return [val for _ in range(n)]


Ltrue = Logic.true
Lfalse = Logic.false
Lx = Logic.x
Lz = Logic.z


class LogicVector:
    width: int = 0
    _vals: list[Logic] = []

    def __init__(self, vals: list[Logic], width: int) -> None:
        self.width = width
        self._vals = copy(vals)
        if len(self._vals) < width:
            pass

    @override
    def __repr__(self) -> str:
        vs = [str(v) for v in self._vals]
        return " ".join(vs[::-1])

    def __getitem__(self, item: int) -> Logic:
        return self._vals[item]

    def __setitem__(self, item: int, val: Logic) -> None:
        self._vals[item] = val

    def bin_op(self, other: "LogicVector", op: BinOp) -> "LogicVector":
        if other.width != self.width:
            other = other.extend(self.width)
        return LogicVector(
            [vs.bin_op(vo, op) for vs, vo in zip(self._vals, other._vals)], self.width
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
        return LogicVector([v.negate() for v in self._vals], self.width)

    def extend(self, by: int) -> "LogicVector":
        diff = by - self.width
        ext = Logic.n_of_val(diff, Logic.false)
        vals = copy(self._vals)
        vals.extend(ext)
        return LogicVector(vals, self.width)

    def sll(self, shift: int) -> "LogicVector":
        shifted = Logic.n_of_val(self.width, Logic.false)

        for bit in range(self.width):
            if bit + shift >= len(shifted):
                break
            shifted[bit + shift] = self._vals[bit]

        return LogicVector(shifted, self.width)

    # TODO: This implementation is definitely bad and needs a rework when I'm less sleepy
    def srl(self, shift: int) -> "LogicVector":
        shifted = Logic.n_of_val(self.width, Logic.false)
        rev = self._vals[::-1]

        for bit in range(self.width):
            if bit + shift >= len(shifted):
                break
            shifted[bit + shift] = rev[bit]

        return LogicVector(shifted[::-1], self.width)

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
        ret = Logic.n_of_val(bitwidth, Logic.false)
        for bit in range(bitwidth):
            mask = 1 << bit
            if (mask & v) != 0:
                ret[bit] = Ltrue
        return LogicVector(ret, bitwidth)
