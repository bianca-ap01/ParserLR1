
from pydantic import BaseModel
from typing import List, Dict, Tuple, Any

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
