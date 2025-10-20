
from __future__ import annotations
from typing import Dict, Iterable, List, Set, Tuple
from collections import defaultdict

EPS = 'ε'
END = '$'
Symbol = str
RHS = Tuple[Symbol, ...]
Prod = Tuple[Symbol, RHS]

class Grammar:
    def __init__(self, start: Symbol, terminals: Iterable[Symbol], nonterminals: Iterable[Symbol]):
        self.start: Symbol = start
        self.terminals: Set[Symbol] = set(terminals) | {END}
        self.nonterminals: Set[Symbol] = set(nonterminals)
        assert start in self.nonterminals
        self.productions: List[Prod] = []
        self.by_lhs: Dict[Symbol, List[RHS]] = defaultdict(list)
        self._first_cache: Dict[Symbol, Set[Symbol]] = {}

    def add(self, lhs: Symbol, rhs: Iterable[Symbol]):
        rhs = tuple(rhs)
        if len(rhs) == 0:
            rhs = (EPS,)
        assert lhs in self.nonterminals
        for s in rhs:
            assert (s in self.terminals) or (s in self.nonterminals) or (s == EPS), f"Símbolo desconocido {s}"
        self.productions.append((lhs, rhs))
        self.by_lhs[lhs].append(rhs)
        self._first_cache.clear()

    # FIRST(X)
    def first(self, X: Symbol) -> Set[Symbol]:
        if X == EPS:
            return {EPS}
        if X in self._first_cache:
            return set(self._first_cache[X])
        if X in self.terminals:
            self._first_cache[X] = {X}
            return {X}
        out: Set[Symbol] = set()
        for rhs in self.by_lhs.get(X, []):
            out |= self.first_of_sequence(rhs)
        self._first_cache[X] = set(out)
        return out

    # FIRST(α)
    def first_of_sequence(self, seq: Iterable[Symbol]) -> Set[Symbol]:
        seq = tuple(seq)
        out: Set[Symbol] = set()
        if not seq:
            return {EPS}
        for sym in seq:
            f = self.first(sym)
            out |= {t for t in f if t != EPS}
            if EPS not in f:
                break
        else:
            out.add(EPS)
        return out