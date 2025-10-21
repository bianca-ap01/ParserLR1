
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
from .grammar import Grammar, Prod

@dataclass
class Action:
    kind: str  # 'shift', 'reduce', 'accept'
    value: Optional[int | Prod] = None

class Tables:
    def __init__(self, G: Grammar, states: List[Set], trans: Dict[Tuple[int, str], int], aug_start: str):
        self.G = G
        self.states = states
        self.trans = trans
        self.aug_start = aug_start
        self.ACTION: Dict[Tuple[int, str], Action] = {}
        self.GOTO: Dict[Tuple[int, str], int] = {}
        self.conflicts: List[Tuple[str, int, str, Action, Action]] = []
        self._build()

    def _set_action(self, i: int, a: str, act: Action):
        key = (i, a)
        if key in self.ACTION and (self.ACTION[key].kind != act.kind or self.ACTION[key].value != act.value):
            old = self.ACTION[key]
            ctype = 'shift/reduce' if {'shift', 'reduce'} == {old.kind, act.kind} else 'reduce/reduce'
            self.conflicts.append((ctype, i, a, old, act))
            return
        self.ACTION[key] = act

    def _build(self):
        G = self.G
        for i, I in enumerate(self.states):
            for a in G.terminals:
                if (i, a) in self.trans:
                    self._set_action(i, a, Action('shift', self.trans[(i, a)]))
            for A in G.nonterminals:
                if (i, A) in self.trans:
                    self.GOTO[(i, A)] = self.trans[(i, A)]
            for it in I:
                if it.is_complete():
                    if it.lhs == self.aug_start and it.la == '$':
                        self._set_action(i, '$', Action('accept'))
                    else:
                        self._set_action(i, it.la, Action('reduce', (it.lhs, it.rhs)))

    def dump_conflicts(self) -> str:
        if not self.conflicts:
            return "No conflicts."
        lines = ["Conflicts:"]
        for ctype, st, sym, old, new in self.conflicts:
            lines.append(f"  • {ctype} at state {st}, on '{sym}': had {old.kind} {old.value}, new {new.kind} {new.value}")
        return "\n".join(lines)

    def dump_tables(self) -> str:
        terms = sorted(self.G.terminals)
        nonterms = sorted(self.G.nonterminals - {self.aug_start})
        hdr = ["st | "] + [f"{t:>8}" for t in terms] + [" || "] + [f"{A:>8}" for A in nonterms]
        lines = ["".join(hdr), "-" * (len("".join(hdr)))]
        for i in range(len(self.states)):
            row = [f"{i:>2} | "]
            for t in terms:
                a = self.ACTION.get((i, t))
                if not a:
                    cell = ''
                elif a.kind == 'shift':
                    cell = f"s{a.value}"
                elif a.kind == 'reduce':
                    lhs, rhs = a.value  # type: ignore
                    cell = f"r[{lhs}→{' '.join(rhs)}]"
                else:
                    cell = 'acc'
                row.append(f"{cell:>8}")
            row.append(" || ")
            for A in nonterms:
                j = self.GOTO.get((i, A))
                row.append(f"{(j if j is not None else ''):>8}")
            lines.append("".join(row))
        return "\n".join(lines)