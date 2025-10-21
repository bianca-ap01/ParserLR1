
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
        # Ensure FIRST sets are computed (iterative fixed-point)
        if not self._first_cache:
            self._compute_all_firsts()
        # EPS handled in the computed sets
        return set(self._first_cache.get(X, set()))

    # FIRST(α)
    def first_of_sequence(self, seq: Iterable[Symbol]) -> Set[Symbol]:
        seq = tuple(seq)
        # Use cached FIRST sets (compute if necessary)
        if not self._first_cache:
            self._compute_all_firsts()
        out: Set[Symbol] = set()
        if not seq:
            return {EPS}
        for sym in seq:
            f = self._first_cache.get(sym, set())
            out |= {t for t in f if t != EPS}
            if EPS not in f:
                break
        else:
            out.add(EPS)
        return out

    def _compute_all_firsts(self) -> None:
        """Compute FIRST sets for all terminals and nonterminals using fixed-point iteration."""
        firsts: Dict[Symbol, Set[Symbol]] = {}
        # Initialize
        for t in self.terminals:
            firsts[t] = {t}
        firsts[EPS] = {EPS}
        for A in self.nonterminals:
            firsts[A] = set()

        changed = True
        while changed:
            changed = False
            # For each production A -> alpha
            for (A, rhs) in self.productions:
                rhs = tuple(rhs)
                # FIRST(alpha)
                if not rhs:
                    seq_first = {EPS}
                else:
                    seq_first: Set[Symbol] = set()
                    for sym in rhs:
                        sym_first = firsts.get(sym, set())
                        seq_first |= {t for t in sym_first if t != EPS}
                        if EPS not in sym_first:
                            break
                    else:
                        seq_first.add(EPS)

                before = len(firsts[A])
                firsts[A] |= seq_first
                if len(firsts[A]) > before:
                    changed = True

        self._first_cache = firsts

    # FOLLOW sets for all nonterminals
    def follow_sets(self) -> Dict[Symbol, Set[Symbol]]:
        """Compute FOLLOW(A) for every nonterminal A.

        Returns a dict mapping nonterminal -> set of terminals (including END '$').
        """
        follows: Dict[Symbol, Set[Symbol]] = {A: set() for A in self.nonterminals}
        # End marker in follow of start symbol
        follows[self.start].add(END)

        changed = True
        while changed:
            changed = False
            for (A, rhs) in self.productions:
                rhs = tuple(rhs)
                for i, B in enumerate(rhs):
                    if B not in self.nonterminals:
                        continue
                    beta = rhs[i+1:]
                    first_beta = self.first_of_sequence(beta)
                    # add FIRST(beta) \ {EPS} to FOLLOW(B)
                    to_add = {t for t in first_beta if t != EPS}
                    before = len(follows[B])
                    follows[B] |= to_add
                    # if beta can derive EPS (or beta empty), add FOLLOW(A)
                    if (not beta) or (EPS in first_beta):
                        follows[B] |= follows[A]
                    if len(follows[B]) > before:
                        changed = True
        return follows