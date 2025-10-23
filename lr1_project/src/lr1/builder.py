
from __future__ import annotations
from typing import Dict, FrozenSet, Iterable, List, Set, Tuple
from collections import deque
from .grammar import Grammar, Symbol, RHS, Prod, EPS, END
from .items import LR1Item

class LR1Builder:
    def __init__(self, G: Grammar):
        self.G = G
        self.aug_start = self._augment_start()

    def _augment_start(self) -> Symbol:
        aug = self.G.start + "'"
        while aug in self.G.nonterminals or aug in self.G.terminals:
            aug += "'"
        self.G.nonterminals.add(aug)
        self.G.by_lhs[aug] = [(self.G.start,)]
        self.G.productions.insert(0, (aug, (self.G.start,)))
        return aug

    def closure(self, I: Iterable[LR1Item]) -> Set[LR1Item]:
        G = self.G
        Iset: Set[LR1Item] = set(I)
        changed = True
        while changed:
            changed = False
            new_items: Set[LR1Item] = set()
            for it in Iset:
                B = it.at_dot()
                if B and B != EPS and B in G.nonterminals:
                    beta = it.rhs[it.dot + 1:]
                    first_beta = G.first_of_sequence(beta)
                    lookaheads: Set[Symbol] = {x for x in first_beta if x != EPS}
                    if EPS in first_beta:
                        lookaheads.add(it.la)
                    for gamma in G.by_lhs.get(B, []):
                        # Treat epsilon-production RHS as empty sequence for items
                        if len(gamma) == 1 and gamma[0] == EPS:
                            gamma = tuple()
                        for b in lookaheads:
                            new_items.add(LR1Item(B, gamma, 0, b))
            before = len(Iset)
            Iset |= new_items
            changed = len(Iset) > before
        return Iset

    def goto(self, I: Iterable[LR1Item], X: Symbol) -> Set[LR1Item]:
        if X == EPS:
            return set()
        moved = [it.advance() for it in I if it.at_dot() == X]
        return self.closure(moved) if moved else set()

    def build_canonical_collection(self) -> Tuple[List[Set[LR1Item]], Dict[Tuple[int, Symbol], int]]:
        start_item = LR1Item(self.aug_start, (self.G.start,), 0, END)
        I0 = self.closure({start_item})

        states: List[Set[LR1Item]] = []
        trans: Dict[Tuple[int, Symbol], int] = {}
        index_of: Dict[FrozenSet[LR1Item], int] = {}

        def idx(s: Set[LR1Item]) -> int:
            key = frozenset(s)
            if key not in index_of:
                index_of[key] = len(states)
                states.append(set(s))
            return index_of[key]

        q = deque()
        i0 = idx(I0)
        q.append(i0)
        while q:
            i = q.popleft()
            I = states[i]
            # Exclude epsilon from transitions in canonical collection
            next_syms = {X for it in I for X in ([it.at_dot()] if it.at_dot() is not None else []) if X != EPS}
            for X in next_syms:
                J = self.goto(I, X)
                if not J:
                    continue
                j = idx(J)
                if (i, X) not in trans:
                    trans[(i, X)] = j
                if j == len(states) - 1:
                    q.append(j)
        return states, trans
