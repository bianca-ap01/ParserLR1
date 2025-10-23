
from typing import List, Dict, Set, Tuple

EPS = 'ε'
_PRECEDENCE = {'*': 3, '+': 3, '?': 3, '.': 2, '|': 1}
_RIGHT_ASSOC = {'*', '+', '?'}

def _is_symbol(c: str) -> bool:
    return c.isalnum() or c == '_'

def add_concat_ops(regex: str) -> str:
    out = []
    prev = ''
    for c in regex:
        if c == ' ':
            continue
        if prev and ( _is_symbol(prev) or prev in ")*+?" ) and ( _is_symbol(c) or c == '(' ):
            out.append('.')
        out.append(c)
        prev = c
    return ''.join(out)

def to_postfix(regex: str) -> str:
    regex = add_concat_ops(regex)
    out: List[str] = []
    stack: List[str] = []
    for c in regex:
        if _is_symbol(c):
            out.append(c)
        elif c == '(':
            stack.append(c)
        elif c == ')':
            while stack and stack[-1] != '(':
                out.append(stack.pop())
            if not stack:
                raise ValueError('Paréntesis desbalanceados')
            stack.pop()
        else:
            while stack and stack[-1] != '(' and (
                _PRECEDENCE[stack[-1]] > _PRECEDENCE[c] or
                (_PRECEDENCE[stack[-1]] == _PRECEDENCE[c] and c not in _RIGHT_ASSOC)
            ):
                out.append(stack.pop())
            stack.append(c)
    while stack:
        op = stack.pop()
        if op in '()':
            raise ValueError('Paréntesis desbalanceados')
        out.append(op)
    return ''.join(out)

class NFA:
    def __init__(self):
        self.next_id = 0
        self.start = self._new_state()
        self.finals: Set[int] = set()
        self.trans: Dict[int, Dict[str, Set[int]]] = {}

    def _new_state(self) -> int:
        i = self.next_id
        self.next_id += 1
        return i

    def add_edge(self, u: int, a: str, v: int):
        self.trans.setdefault(u, {}).setdefault(a, set()).add(v)

def thompson_from_postfix(post: str) -> NFA:
    stack: List[Tuple[int, Set[int]]] = []
    master = NFA()

    def lit(a: str):
        s = master._new_state()
        f = master._new_state()
        # Treat 'ε' as epsilon transition label
        master.add_edge(s, (EPS if a == 'ε' else a), f)
        return (s, {f})

    for c in post:
        if _is_symbol(c):
            stack.append(lit(c))
        elif c == '.':
            b = stack.pop(); a = stack.pop()
            for u in a[1]:
                master.add_edge(u, EPS, b[0])
            stack.append((a[0], b[1]))
        elif c == '|':
            b = stack.pop(); a = stack.pop()
            s = master._new_state(); f = master._new_state()
            master.add_edge(s, EPS, a[0])
            master.add_edge(s, EPS, b[0])
            for u in a[1]:
                master.add_edge(u, EPS, f)
            for u in b[1]:
                master.add_edge(u, EPS, f)
            stack.append((s, {f}))
        elif c == '*':
            a = stack.pop()
            s = master._new_state(); f = master._new_state()
            master.add_edge(s, EPS, a[0])
            master.add_edge(s, EPS, f)
            for u in a[1]:
                master.add_edge(u, EPS, a[0])
                master.add_edge(u, EPS, f)
            stack.append((s, {f}))
        elif c == '+':
            a = stack.pop()
            s = master._new_state(); f = master._new_state()
            master.add_edge(s, EPS, a[0])
            for u in a[1]:
                master.add_edge(u, EPS, a[0])
                master.add_edge(u, EPS, f)
            stack.append((s, {f}))
        elif c == '?':
            a = stack.pop()
            s = master._new_state(); f = master._new_state()
            master.add_edge(s, EPS, a[0])
            master.add_edge(s, EPS, f)
            for u in a[1]:
                master.add_edge(u, EPS, f)
            stack.append((s, {f}))
        else:
            raise ValueError(f"Operador no soportado: {c}")

    if len(stack) != 1:
        raise ValueError('ER inválida')
    start, finals = stack.pop()
    master.start = start
    master.finals = finals
    return master

def epsilon_closure(trans: Dict[int, Dict[str, Set[int]]], S: Set[int]) -> Set[int]:
    stack = list(S)
    seen = set(S)
    while stack:
        u = stack.pop()
        for v in trans.get(u, {}).get(EPS, set()):
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return seen
