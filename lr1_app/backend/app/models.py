
from pydantic import BaseModel
from typing import List, Dict, Tuple, Any, Optional

class GrammarRequest(BaseModel):
    text: str  # archivo de gramática estilo labs

class RegexRequest(BaseModel):
    pattern: str  # expresión regular

class NFATransition(BaseModel):
    src: int
    sym: str  # 'ε' para epsilon
    dst: int

class NFAResponse(BaseModel):
    states: List[int]
    start: int
    finals: List[int]
    transitions: List[NFATransition]
    eclosure: Dict[int, List[int]]

class DFAResponse(BaseModel):
    states: List[str]
    start: str
    finals: List[str]
    alphabet: List[str]
    transitions: List[Dict[str, str]]
    subset_table: List[Dict[str, Any]]

class LR1Response(BaseModel):
    action: Dict[str, Dict[str, str]]
    goto: Dict[str, Dict[str, int]]
    conflicts: List[Dict[str, Any]]
    states: List[Dict[str, Any]]
    transitions: List[Dict[str, Any]]
    grammar_augmented: List[str]
    # Analysis fields (augmented grammar)
    terminals: List[str]
    nonterminals: List[str]
    first: Dict[str, List[str]]
    follow: Dict[str, List[str]]
    # Optional visualization of LR(1) items NFA
    items_nfa: Dict[str, Any] | None = None
    # Optional visualization of LR(1) states DFA (canonical collection)
    items_dfa: Dict[str, Any] | None = None

class ParseRequest(BaseModel):
    text: str
    program: Optional[str] = None  # raw source to tokenize (requires LEXER)
    tokens: Optional[List[str]] = None  # explicit token types (spaces-separated in UI)

class TraceStep(BaseModel):
    stack: List[int]
    lookahead: str
    remaining: List[str]
    action: str

class ParseTraceResponse(BaseModel):
    steps: List[TraceStep]
    tokens: List[str]
    accepted: bool
    message: Optional[str] = None
