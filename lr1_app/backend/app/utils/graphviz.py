from typing import Dict, Set, List, Union, Any
import base64
import graphviz

def automaton_to_dot(
    states: Union[List[Any], Set[Any]], 
    start: Any, 
    finals: Union[List[Any], Set[Any]], 
    transitions: Dict[Any, Dict[str, Any]], 
    is_nfa: bool = True
) -> str:
    """Convert an automaton (NFA/DFA) to DOT format for Graphviz"""
    dot = graphviz.Digraph(
        graph_attr={'rankdir': 'LR'}, 
        node_attr={'shape': 'circle'}
    )
    
    # Add all states
    for state in states:
        if state in finals:
            dot.node(str(state), str(state), shape='doublecircle')
        else:
            dot.node(str(state), str(state))
    
    # Add start state indicator
    dot.node('start', '', shape='point')
    dot.edge('start', str(start))
    
    # Add transitions
    if is_nfa:
        # For NFA - handle multiple transitions and ε
        for from_state, paths in transitions.items():
            for symbol, to_states in paths.items():
                if isinstance(to_states, (list, set)):
                    for to_state in to_states:
                        dot.edge(str(from_state), str(to_state), 
                               label='ε' if symbol == 'eps' else symbol)
                else:
                    dot.edge(str(from_state), str(to_states),
                            label='ε' if symbol == 'eps' else symbol)
    else:
        # For DFA - single transition per symbol
        for from_state, paths in transitions.items():
            for symbol, to_state in paths.items():
                dot.edge(str(from_state), str(to_state), label=symbol)
    
    return dot

def automaton_to_base64(dot: graphviz.Digraph) -> str:
    """Convert a Graphviz dot graph to base64 PNG image"""
    png_data = dot.pipe(format='png')
    return base64.b64encode(png_data).decode('utf-8')