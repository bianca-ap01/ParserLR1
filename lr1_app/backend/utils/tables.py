
from typing import Dict

def action_to_dict(ACTION) -> Dict[str, Dict[str, str]]:
    out: Dict[str, Dict[str, str]] = {}
    for (i, a), act in ACTION.items():
        row = out.setdefault(str(i), {})
        if act.kind == 'shift':
            row[str(a)] = f"s{act.value}"
        elif act.kind == 'reduce':
            lhs, rhs = act.value
            row[str(a)] = f"r[{lhs}→{' '.join(rhs)}]"
        else:
            row[str(a)] = 'acc'
    return out

def goto_to_dict(GOTO) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Dict[str, int]] = {}
    for (i, A), j in GOTO.items():
        out.setdefault(str(i), {})[str(A)] = int(j)
    return out