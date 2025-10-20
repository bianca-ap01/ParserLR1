
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
from .grammar import Symbol, RHS

@dataclass(frozen=True)
class LR1Item:
    lhs: Symbol
    rhs: RHS
    dot: int
    la: Symbol  # lookahead

    def at_dot(self) -> Optional[Symbol]:
        return self.rhs[self.dot] if self.dot < len(self.rhs) else None

    def advance(self) -> 'LR1Item':
        return LR1Item(self.lhs, self.rhs, self.dot + 1, self.la)

    def is_complete(self) -> bool:
        return self.dot >= len(self.rhs)