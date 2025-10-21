
from typing import Dict, Set, List, Tuple
from .regex_thompson import EPS, epsilon_closure

def nfa_to_dfa(trans: Dict[int, Dict[str, Set[int]]], start: int, finals: Set[int]) -> Tuple[List[Set[int]], Dict[Tuple[int, str], int], int, Set[int], List[Dict[str, str]]]:
    alphabet: List[str] = sorted({a for m in trans.values() for a in m.keys() if a != EPS})

    def move(S: Set[int], a: str) -> Set[int]:
        dest = set()
        for u in S:
            dest |= trans.get(u, {}).get(a, set())
        return dest

    start_set = epsilon_closure(trans, {start})
    states: List[Set[int]] = []
    index: Dict[Tuple[int, ...], int] = {}
    def idx(S: Set[int]) -> int:
        key = tuple(sorted(S))
        if key not in index:
            index[key] = len(states)
            states.append(set(S))
        return index[key]

    subset_table: List[Dict[str, str]] = []
    q = [start_set]
    idx0 = idx(start_set)
    front = 0
    delta: Dict[Tuple[int, str], int] = {}

    while front < len(q):
        S = q[front]; front += 1
        i = idx(S)
        row = {'state': str(set(S))}
        for a in alphabet:
            U = set()
            for u in S:
                U |= trans.get(u, {}).get(a, set())
            U = epsilon_closure(trans, U)
            j = idx(U)
            delta[(i, a)] = j
            row[a] = str(set(U))
            if U not in q:
                q.append(U)
        subset_table.append(row)

    start_i = idx0
    final_i: Set[int] = set()
    for i, S in enumerate(states):
        if S & finals:
            final_i.add(i)

    return states, delta, start_i, final_i, subset_table