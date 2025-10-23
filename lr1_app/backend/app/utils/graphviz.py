from typing import Dict, Set, List, Union, Any
import base64
try:
    import graphviz  # type: ignore
except Exception:  # pragma: no cover
    graphviz = None  # Lazy handling if library is missing


def automaton_to_dot(
    states: Union[List[Any], Set[Any]],
    start: Any,
    finals: Union[List[Any], Set[Any]],
    transitions: Dict[Any, Dict[str, Any]],
    is_nfa: bool = True,
):
    if graphviz is None:
        raise RuntimeError("graphviz library not installed")

    dot = graphviz.Digraph(
        graph_attr={'rankdir': 'LR'},
        node_attr={'shape': 'ellipse'},
    )

    # Add states (uniform appearance, no double circles)
    for state in states:
        dot.node(str(state), str(state))

    # Start indicator
    dot.node('start', '', shape='point')
    dot.edge('start', str(start))

    # Transitions
    if is_nfa:
        for u, paths in transitions.items():
            for sym, dsts in paths.items():
                is_eps = str(sym) in ('eps', 'ε', '��')
                if isinstance(dsts, (list, set)):
                    for v in dsts:
                        dot.edge(str(u), str(v), label=('ε' if is_eps else str(sym)))
                else:
                    dot.edge(str(u), str(dsts), label=('ε' if is_eps else str(sym)))
    else:
        # DFA: no epsilon transitions should be drawn
        for u, paths in transitions.items():
            for sym, v in paths.items():
                s = str(sym)
                if s in ('eps', 'ε', '��'):
                    # skip epsilon on DFA
                    continue
                dot.edge(str(u), str(v), label=s)

    return dot


def automaton_to_base64(dot) -> str:
    if graphviz is None:
        return ''
    png_data = dot.pipe(format='png')
    return base64.b64encode(png_data).decode('utf-8')
