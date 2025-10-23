from typing import Dict
from lr1.grammar import EPS as G_EPS

def action_to_dict(ACTION) -> Dict[str, Dict[str, str]]:
    out: Dict[str, Dict[str, str]] = {}
    for (i, a), act in ACTION.items():
        row = out.setdefault(str(i), {})
        if act.kind == 'shift':
            row[str(a)] = f"s{act.value}"
        elif act.kind == 'reduce':
            lhs, rhs = act.value
            body = 'ε' if (len(rhs) == 1 and rhs[0] == G_EPS) else ' '.join(rhs)
            row[str(a)] = f"r[{lhs} -> {body}]"
        else:
            row[str(a)] = 'acc'
    return out

def goto_to_dict(GOTO) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Dict[str, int]] = {}
    for (i, A), j in GOTO.items():
        out.setdefault(str(i), {})[str(A)] = int(j)
    return out

