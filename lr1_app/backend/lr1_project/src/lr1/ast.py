
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Node:
    sym: str
    children: List['Node']
    lexeme: Optional[str] = None

    def pretty(self, indent: str = '') -> str:
        here = f"{indent}{self.sym}" + (f":{self.lexeme}" if self.lexeme else '')
        lines = [here]
        for ch in self.children:
            lines.append(ch.pretty(indent + '  '))
        return "\n".join(lines)