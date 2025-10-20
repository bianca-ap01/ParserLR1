
from __future__ import annotations
import re
from typing import Dict, List, Tuple
from .grammar import Grammar

_SECTION_RE = re.compile(r"^(START|NONTERMINALS|TERMINALS|PRODUCTIONS|LEXER):\s*(.*)$")
_LEXER_LINE_RE = re.compile(r"^(.+?):\s*/(.+?)/\s*(skip)?$")

class GrammarSpec:
    def __init__(self):
        self.start = ''
        self.nonterms: List[str] = []
        self.terms: List[str] = []
        self.prods: List[Tuple[str, List[str]]] = []
        self.lex_rules: List[Tuple[str, str, bool]] = []  # (terminal, regex, skip)

    def to_grammar(self) -> Grammar:
        G = Grammar(self.start, self.terms, self.nonterms)
        for A, rhs in self.prods:
            G.add(A, rhs)
        return G

def _strip_quotes(s: str) -> str:
    s = s.strip()
    if (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')):
        return s[1:-1]
    return s

def load_grammar_file(path: str) -> Tuple[GrammarSpec, Grammar]:
    with open(path, 'r', encoding='utf-8') as f:
        lines = [ln.rstrip() for ln in f]

    current = None
    spec = GrammarSpec()
    prod_lines: List[str] = []

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
            term = _strip_quotes(name)
            regex = mm.group(2)
            skip = bool(mm.group(3))
            spec.lex_rules.append((term, regex, skip))
        else:
            raise ValueError(f"Línea fuera de sección: {raw}")

    # Parse productions block
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

    G = spec.to_grammar()
    return spec, G