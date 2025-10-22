
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
from .models import GrammarRequest, RegexRequest, NFAResponse, NFATransition, DFAResponse, LR1Response
from .utils.tables import action_to_dict, goto_to_dict

from lr1.grammar_io import GrammarSpec
from lr1.builder import LR1Builder
from lr1.tables import Tables

from .lex.regex_thompson import to_postfix, thompson_from_postfix, EPS, epsilon_closure
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

def load_grammar_from_text(text: str):
    lines = [ln.rstrip("\n") for ln in text.splitlines()]
    spec = GrammarSpec()
    prod_lines: List[str] = []
    current = None
    # Soporta BNF simple sin encabezados (solo producciones)
    saw_header = any(_SECTION_RE.match(ln) for ln in lines if ln.strip())
    if not saw_header:
        for raw in lines:
            if not raw.strip():
                continue
            prod_lines.append(raw.strip())
        # Parsear producciones
        for ln in prod_lines:
            if '->' not in ln:
                continue
            lhs, rhs = ln.split('->', 1)
            A = lhs.strip()
            alts = [alt.strip() for alt in rhs.split('|')]
            for alt in alts:
                if alt == '' or alt.lower() == '��' or alt == '��':
                    spec.prods.append((A, []))
                else:
                    symbols = [s for s in alt.split() if s]
                    spec.prods.append((A, symbols))
        # Inferir START/NONTERMINALS/TERMINALS
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
    for ln in prod_lines:
        if '->' not in ln:
            continue
        lhs, rhs = ln.split('->', 1)
        A = lhs.strip()
        alts = [alt.strip() for alt in rhs.split('|')]
        for alt in alts:
            if alt == '' or alt.lower() == 'ε':
                spec.prods.append((A, []))
            else:
                symbols = [s for s in alt.split() if s]
                spec.prods.append((A, symbols))
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

    return LR1Response(
        action=action_to_dict(tables.ACTION),
        goto=goto_to_dict(tables.GOTO),
        conflicts=[{'type': c[0], 'state': c[1], 'symbol': c[2]} for c in tables.conflicts],
        states=states_out,
        transitions=trans_out,
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
