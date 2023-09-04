from enum import Enum


class EventType(Enum):
    START = "START"
    END = "END"
    TASK = "TASK"
    EXCLUSIVE_OR = "EXCLUSIVE_OR"
    PARALLEL = "PARALLEL"
    TOTAL = "TOTAL"


class ActionType(Enum):
    SKIP = "SKIP"
    INSERT = "INSERT"
    TO_PARALLEL = "TO_PARALLEL"
    TO_SERIES = "TO_SERIES"


class DistributionType(Enum):
    FIXED = "FIXED"
    NORMAL = "NORMAL"
    UNIFORM = "UNIFORM"


class EqualityType(Enum):
    GT = ">"
    GET = ">="
    LT = "<"
    LET = "<="
    EQ = "=="
    NEQ = "!="

    def compare(self, a: float, b: float) -> bool:
        match self.value:
            case ">":
                return a > b
            case ">=":
                return a >= b
            case "<":
                return a < b
            case "<=":
                return a <= b
            case "==":
                return a == b
            case "!=":
                return a != b
            case _:
                raise ValueError("Unknown EqualityType in compare call!")
