
from __future__ import annotations
from typing import List, Tuple, Optional
from .tables import Tables
from .ast import Node
from .grammar import END, EPS

class Parser:
    def __init__(self, tables: Tables, build_tree: bool = True):
        self.T = tables
        self.build_tree = build_tree

    def parse(self, tokens: List[Tuple[str, Optional[str]] | str]) -> Optional[Node]:
        norm: List[Tuple[str, Optional[str]]] = []
        for tk in tokens:
            if isinstance(tk, str):
                norm.append((tk, tk))
            else:
                t, lx = tk
                norm.append((t, lx))
        norm.append((END, END))

        states: List[int] = [0]
        nodes: List[Node] = []
        i = 0
        while True:
            s = states[-1]
            a_type, a_lex = norm[i]
            act = self.T.ACTION.get((s, a_type))
            if not act:
                expected = sorted({sym for (st, sym) in self.T.ACTION.keys() if st == s})
                raise SyntaxError(f"Unexpected token '{a_type}' at pos {i}. Expected: {expected}")

            if act.kind == 'shift':
                if self.build_tree and a_type != END:
                    nodes.append(Node(a_type, [], a_lex))
                states.append(int(act.value))  # type: ignore
                i += 1
            elif act.kind == 'reduce':
                lhs, rhs = act.value  # type: ignore
                k = 0 if rhs == (EPS,) else len(rhs)
                children: List[Node] = []
                if self.build_tree:
                    for _ in range(k):
                        children.append(nodes.pop())
                    children.reverse()
                for _ in range(k):
                    states.pop()
                s = states[-1]
                j = self.T.GOTO.get((s, lhs))
                if j is None:
                    raise RuntimeError(f"Missing GOTO for state {s}, lhs {lhs}")
                states.append(j)
                if self.build_tree:
                    nodes.append(Node(lhs, [] if rhs == (EPS,) else children))
            else:
                return nodes[0] if (self.build_tree and nodes) else None