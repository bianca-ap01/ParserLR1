
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
        self._first_visiting: Set[Symbol] = set()

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

    def _compute_first_all(self) -> None:
        # Initialize FIRST sets
        firsts: Dict[Symbol, Set[Symbol]] = {}
        for t in self.terminals:
            firsts[t] = {t}
        for A in self.nonterminals:
            firsts.setdefault(A, set())
        # Fixed-point iteration
        changed = True
        while changed:
            changed = False
            for A, rhs in self.productions:
                # epsilon production
                if len(rhs) == 1 and rhs[0] == EPS:
                    if EPS not in firsts[A]:
                        firsts[A].add(EPS)
                        changed = True
                    continue
                # general case
                add_eps = True
                for Y in rhs:
                    Fy = firsts.get(Y, {Y} if Y in self.terminals else set())
                    # add FIRST(Y) minus EPS
                    size_before = len(firsts[A])
                    firsts[A] |= {s for s in Fy if s != EPS}
                    if len(firsts[A]) > size_before:
                        changed = True
                    if EPS not in Fy:
                        add_eps = False
                        break
                if add_eps:
                    if EPS not in firsts[A]:
                        firsts[A].add(EPS)
                        changed = True
        self._first_cache = {k: set(v) for k, v in firsts.items()}

    # FIRST(X)
    def first(self, X: Symbol) -> Set[Symbol]:
        if X == EPS:
            return {EPS}
        if X not in self._first_cache:
            self._compute_first_all()
        if X in self._first_cache:
            return set(self._first_cache[X])
        if X in self.terminals:
            return {X}
        return set()

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

    # FOLLOW sets for all nonterminals
    def follow_sets(self) -> Dict[Symbol, Set[Symbol]]:
        follow: Dict[Symbol, Set[Symbol]] = {A: set() for A in self.nonterminals}
        # $ is in terminals by construction; add to start symbol FOLLOW
        follow[self.start].add(END)

        changed = True
        while changed:
            changed = False
            for A, rhs in self.productions:
                # Iterate each position in RHS
                for i, B in enumerate(rhs):
                    if B not in self.nonterminals:
                        continue
                    beta = rhs[i+1:]
                    first_beta = self.first_of_sequence(beta)
                    # Add FIRST(beta) \ {EPS}
                    before = len(follow[B])
                    follow[B] |= {x for x in first_beta if x != EPS}
                    if len(follow[B]) > before:
                        changed = True
                    # If beta can derive EPS or empty, add FOLLOW(A)
                    if not beta or EPS in first_beta:
                        before2 = len(follow[B])
                        follow[B] |= follow[A]
                        if len(follow[B]) > before2:
                            changed = True
        return follow
