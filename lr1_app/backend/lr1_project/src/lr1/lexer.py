
from __future__ import annotations
import re
from typing import List, Tuple

class Lexer:
    def __init__(self, rules: List[Tuple[str, str, bool]]):
        # rules: (terminal, regex, skip)
        parts = []
        self.term_by_group = []
        self.skip_groups = set()
        for idx, (term, rx, skip) in enumerate(rules):
            name = f"G{idx}"
            parts.append(f"(?P<{name}>{rx})")
            self.term_by_group.append((name, term))
            if skip:
                self.skip_groups.add(name)
        self.master = re.compile("|".join(parts))

    def tokenize(self, text: str) -> List[Tuple[str, str]]:
        out: List[Tuple[str, str]] = []
        pos = 0
        mo = self.master.match(text, pos)
        while mo:
            name = mo.lastgroup
            lexeme = mo.group(name)
            if name not in self.skip_groups:
                for g, term in self.term_by_group:
                    if g == name:
                        out.append((term, lexeme))
                        break
            pos = mo.end()
            mo = self.master.match(text, pos)
        if pos != len(text):
            raise SyntaxError(f"Lexer: input no reconocido desde pos {pos}: {text[pos:pos+20]!r}")
        return out