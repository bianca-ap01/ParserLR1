from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List

from .models import GrammarRequest, RegexRequest, NFAResponse, NFATransition, DFAResponse, LR1Response
from .utils.tables import action_to_dict, goto_to_dict

from lr1.grammar_io import GrammarSpec
from lr1.builder import LR1Builder
from lr1.tables import Tables
from lr1.grammar import EPS as G_EPS
from lr1.items import LR1Item

from .lex.regex_thompson import to_postfix, thompson_from_postfix, EPS as RE_EPS, epsilon_closure
from .lex.dfa_subset import nfa_to_dfa

import re

app = FastAPI(title="LR(1) Fullstack API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_SECTION_RE = re.compile(r"^(START|NONTERMINALS|TERMINALS|PRODUCTIONS|LEXER):\s*(.*)$")
_LEXER_LINE_RE = re.compile(r"^(.+?):\s*/(.+?)/\s*(skip)?$")


def load_grammar_from_text(text: str) -> GrammarSpec:
    lines = [ln.rstrip("\n") for ln in text.splitlines()]
    spec = GrammarSpec()
    prod_lines: List[str] = []
    current = None

    # Detectar si hay encabezados; si no, tratamos todo como producciones
    saw_header = any(_SECTION_RE.match(ln) for ln in lines if ln.strip())

    if not saw_header:
        for raw in lines:
            if not raw.strip():
                continue
            prod_lines.append(raw.strip())
    else:
        for raw in lines:
            if not raw.strip():
                continue
            m = _SECTION_RE.match(raw)
            if m:
                current = m.group(1)
                rest = m.group(2)
                if current == 'START':
                    spec.start = rest.strip()
                elif current == 'NONTERMINALS':
                    spec.nonterms = [t for t in rest.split() if t]
                elif current == 'TERMINALS':
                    spec.terms = [t for t in rest.split() if t]
                elif current == 'PRODUCTIONS':
                    prod_lines.clear()
                elif current == 'LEXER':
                    pass
                continue
            if current == 'PRODUCTIONS':
                prod_lines.append(raw.strip())
            elif current == 'LEXER':
                mm = _LEXER_LINE_RE.match(raw.strip())
                if not mm:
                    raise ValueError(f"Línea de lexer inválida: {raw}")
                name = mm.group(1).strip()
                term = name[1:-1] if (name.startswith("'") and name.endswith("'")) or (name.startswith('"') and name.endswith('"')) else name
                regex = mm.group(2)
                skip = bool(mm.group(3))
                spec.lex_rules.append((term, regex, skip))
            else:
                raise ValueError(f"Línea fuera de sección: {raw}")

    # Parseo de producciones
    for ln in prod_lines:
        if '->' not in ln:
            continue
        lhs, rhs = ln.split('->', 1)
        A = lhs.strip()
        alts = [alt.strip() for alt in rhs.split('|')]
        alts = [("" if a == 'ε' or a.casefold() in {'epsilon','eps'} else a) for a in alts]
        for alt in alts:
            if alt == '' or alt.lower() == '��' or alt == '��':
                spec.prods.append((A, []))
            else:
                symbols = [s for s in alt.split() if s]
                spec.prods.append((A, symbols))

    # Si no hubo encabezados, inferir START/NONTERMINALS/TERMINALS
    if not saw_header:
        lhs_order = [A for (A, _) in spec.prods]
        if lhs_order:
            spec.start = lhs_order[0]
        nonterms = {A for (A, _) in spec.prods}
        spec.nonterms = sorted(list(nonterms))
        rhs_syms = set()
        for (_, rhs) in spec.prods:
            for s in rhs:
                if s != '��':
                    rhs_syms.add(s)
        spec.terms = sorted([s for s in rhs_syms if s not in nonterms])

    return spec


@app.post('/lr1/build', response_model=LR1Response)
def lr1_build(req: GrammarRequest):
    spec = load_grammar_from_text(req.text)
    G = spec.to_grammar()
    builder = LR1Builder(G)
    states, trans = builder.build_canonical_collection()
    tables = Tables(G, states, trans, builder.aug_start)

    states_out: List[Dict[str, Any]] = []
    for i, I in enumerate(states):
        items = []
        for it in sorted(I, key=lambda z: (z.lhs, z.rhs, z.dot, z.la)):
            items.append({'lhs': it.lhs, 'rhs': list(it.rhs), 'dot': it.dot, 'la': it.la})
        states_out.append({'state': i, 'items': items})

    trans_out = [{'from': i, 'symbol': X, 'to': j} for (i, X), j in trans.items()]

    # Gramática aumentada como lista de strings
    grammar_augmented = []
    for lhs, rhs in G.productions:
        if len(rhs) == 1 and (rhs[0] == G_EPS or rhs[0] == 'ε'):
            rhs_str = 'ε'
        else:
            rhs_str = ' '.join(rhs)
        grammar_augmented.append(f"{lhs} -> {rhs_str}")

    # Símbolos, FIRST y FOLLOW (de la gramática aumentada)
    nonterminals = sorted(list(G.nonterminals))
    terminals = sorted([t for t in G.terminals if t != '$'])
    show_syms = nonterminals + terminals
    first_map = {X: sorted(list(G.first(X))) for X in show_syms}
    follow_sets = G.follow_sets()
    # Asegurar que el símbolo inicial aumentado tenga $ en FOLLOW
    try:
        aug = builder.aug_start
        if aug not in follow_sets:
            follow_sets[aug] = set()
        follow_sets[aug].add('$')
    except Exception:
        pass
    follow_map = {A: sorted(list(follow_sets.get(A, set()))) for A in nonterminals}

    # Construir AFN de ítems LR(1) (estados = ítems, transiciones por símbolo o epsilon por cierre)
    def item_key(it: LR1Item) -> str:
        rhs = ' '.join(it.rhs)
        return f"{it.lhs}|{rhs}|{it.dot}|{it.la}"

    def item_label(it: LR1Item) -> str:
        def filt(xs):
            return [x for x in xs if x not in (G_EPS, 'ε', 'eps') and ('�' not in str(x))]
        rhs = filt(list(it.rhs))
        left = ' '.join(rhs[:it.dot])
        right = ' '.join(rhs[it.dot:])
        parts = []
        if left:
            parts.append(left)
        parts.append('.')
        if right:
            parts.append(right)
        body = ' '.join(parts)
        return f"{it.lhs} -> {body}, {it.la}"

    start_item = LR1Item(builder.aug_start, (G.start,), 0, '$')
    queue: list[LR1Item] = [start_item]
    seen: dict[str, LR1Item] = {item_key(start_item): start_item}
    labels: dict[str, str] = {item_key(start_item): item_label(start_item)}
    transitions: dict[str, dict[str, set[str]]] = {}
    finals: set[str] = set()

    while queue:
        it = queue.pop(0)
        k = item_key(it)
        transitions.setdefault(k, {})
        # final si S' -> S · , $
        if it.lhs == builder.aug_start and it.dot == len(it.rhs) and it.la == '$':
            finals.add(k)
        X = it.rhs[it.dot] if it.dot < len(it.rhs) else None
        if X is None:
            continue
        # avance (consumo de símbolo)
        it2 = it.advance()
        k2 = item_key(it2)
        if k2 not in seen:
            seen[k2] = it2
            labels[k2] = item_label(it2)
            queue.append(it2)
        # Skip epsilon-labeled advances
        if str(X) not in (G_EPS, 'ε', 'eps'):
            transitions[k].setdefault(str(X), set()).add(k2)
        # cierre si X es no terminal
        if X in G.nonterminals:
            beta = it.rhs[it.dot + 1:]
            first_beta = G.first_of_sequence(beta)
            lks = {x for x in first_beta if x != G_EPS}
            if G_EPS in first_beta:
                lks.add(it.la)
            for gamma in G.by_lhs.get(X, []):
                if len(gamma) == 1 and gamma[0] == G_EPS:
                    gamma = tuple()
                for b in lks:
                    dest = LR1Item(X, gamma, 0, b)
                    kd = item_key(dest)
                    if kd not in seen:
                        seen[kd] = dest
                        labels[kd] = item_label(dest)
                        queue.append(dest)
                    transitions[k].setdefault('eps', set()).add(kd)

    # Armar DOT e imagen usando util existente
    state_ids = list(seen.keys())
    state_labels = {k: labels[k] for k in state_ids}
    # Convertir transiciones a formato requerido por graphviz util (con labels de estados)
    trans_for_dot: dict[str, dict[str, list[str]]] = {}
    for src_k, mp in transitions.items():
        src_label = state_labels[src_k]
        for sym, dests in mp.items():
            for dk in dests:
                dst_label = state_labels[dk]
                trans_for_dot.setdefault(src_label, {}).setdefault(sym, []).append(dst_label)
    states_for_dot = list(state_labels.values())
    start_label = state_labels[item_key(start_item)]
    finals_labels = [state_labels[k] for k in finals]
    # Render image (optional if graphviz installed)
    try:
        from .utils.graphviz import automaton_to_dot, automaton_to_base64
        dot = automaton_to_dot(states_for_dot, start_label, finals_labels, trans_for_dot, is_nfa=True)
        img_nfa = automaton_to_base64(dot)
    except Exception:
        img_nfa = None
    items_nfa = {
        'states': states_for_dot,
        'start': start_label,
        'finals': finals_labels,
        'transitions': trans_for_dot,
        'image': img_nfa,
    }

    # DFA de estados LR(1) (colección canónica)
    try:
        # Etiquetas con items por estado
        def label_state(idx: int) -> str:
            I = states[idx]
            lines = []
            for it in sorted(I, key=lambda z: (z.lhs, z.rhs, z.dot, z.la)):
                rhs = [x for x in it.rhs if x not in (G_EPS, 'ε', 'eps') and ('�' not in str(x))]
                left = ' '.join(rhs[:it.dot])
                right = ' '.join(rhs[it.dot:])
                parts = []
                if left:
                    parts.append(left)
                parts.append('.')
                if right:
                    parts.append(right)
                body = ' '.join(parts)
                lines.append(f"{it.lhs} -> {body}, {it.la}")
            return f"{idx}\n" + "\n".join(lines)

        state_label_map = {i: label_state(i) for i in range(len(states))}
        dfa_states = [state_label_map[i] for i in range(len(states))]
        dfa_start = state_label_map[0]
        dfa_finals = []
        for i, I in enumerate(states):
            if any((it.lhs == builder.aug_start and it.dot == len(it.rhs) and it.la == '$') for it in I):
                dfa_finals.append(state_label_map[i])
        dfa_trans: Dict[str, Dict[str, str]] = {}
        for (i, X), j in trans.items():
            src = state_label_map[i]
            dst = state_label_map[j]
            dfa_trans.setdefault(src, {})[str(X)] = dst
        try:
            from .utils.graphviz import automaton_to_dot, automaton_to_base64
            dot_dfa = automaton_to_dot(dfa_states, dfa_start, dfa_finals, dfa_trans, is_nfa=False)
            img_dfa = automaton_to_base64(dot_dfa)
        except Exception:
            img_dfa = None
        items_dfa = {
            'states': dfa_states,
            'start': dfa_start,
            'finals': dfa_finals,
            'transitions': dfa_trans,
            'image': img_dfa,
        }
    except Exception:
        items_dfa = None

    return LR1Response(
        action=action_to_dict(tables.ACTION),
        goto=goto_to_dict(tables.GOTO),
        conflicts=[{'type': c[0], 'state': c[1], 'symbol': c[2]} for c in tables.conflicts],
        states=states_out,
        transitions=trans_out,
        grammar_augmented=grammar_augmented,
        terminals=terminals,
        nonterminals=nonterminals,
        first=first_map,
        follow=follow_map,
        items_nfa=items_nfa,
        items_dfa=items_dfa,
    )


@app.post('/lex/regex2nfa', response_model=NFAResponse)
def regex_to_nfa(req: RegexRequest):
    post = to_postfix(req.pattern)
    nfa = thompson_from_postfix(post)
    all_states = set(nfa.trans.keys()) | {nfa.start}
    for m in nfa.trans.values():
        for dests in m.values():
            all_states |= set(dests)
    states = sorted(all_states)
    ecl = {i: sorted(list(epsilon_closure(nfa.trans, {i}))) for i in states}
    transitions = []
    for u, m in nfa.trans.items():
        for a, dests in m.items():
            for v in dests:
                transitions.append(NFATransition(src=u, sym=a, dst=v))
    return NFAResponse(states=states, start=nfa.start, finals=sorted(list(nfa.finals)), transitions=transitions, eclosure=ecl)


@app.post('/lex/nfa2dfa', response_model=DFAResponse)
def nfa_to_dfa_endpoint(nfa: NFAResponse):
    trans: Dict[int, Dict[str, set]] = {}
    for t in nfa.transitions:
        trans.setdefault(t.src, {}).setdefault(t.sym, set()).add(t.dst)
    finals = set(nfa.finals)
    states, delta, start_i, final_i, subset_table = nfa_to_dfa(trans, nfa.start, finals)

    alphabet = sorted({a for (_, a) in delta.keys()})
    def enc(S: set) -> str:
        return '{' + ','.join(str(x) for x in sorted(S)) + '}'

    rows = []
    for i, S in enumerate(states):
        row = {'state': enc(S)}
        for a in alphabet:
            j = delta.get((i, a))
            row[a] = enc(states[j]) if j is not None else '{}'
        rows.append(row)

    return DFAResponse(
        states=[enc(S) for S in states],
        start=enc(states[start_i]),
        finals=[enc(states[i]) for i in sorted(final_i)],
        alphabet=alphabet,
        transitions=rows,
        subset_table=subset_table,
    )
