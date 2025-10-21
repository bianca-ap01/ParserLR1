
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

class AutomatonSuccess(BaseModel):
    states: List[Any]
    start: Any
    finals: List[Any]
    transitions: Dict[Any, Dict[str, Any]]
    image: Optional[str] = None  # base64 imagen PNG

class AutomatonError(BaseModel):
    error: str

class AutomatonBase(BaseModel):
    success: Optional[AutomatonSuccess] = None
    error: Optional[str] = None

class NFAResponse(AutomatonBase):
    pass

class DFAResponse(AutomatonBase):
    alphabet: Optional[List[str]] = None  # Solo presente en caso de éxito

class LR1Response(BaseModel):
    action: Dict[str, Dict[str, str]]
    goto: Dict[str, Dict[str, int]]
    conflicts: List[Dict[str, Any]]
    states: List[Dict[str, Any]]
    transitions: List[Dict[str, Any]]
    # Analysis fields
    terminals: List[str]
    nonterminals: List[str]
    first: Dict[str, List[str]]
    follow: Dict[str, List[str]]
    grammar_augmented: List[str]  # Producciones de la gramática aumentada (strings)
    nfa: Dict[str, AutomatonBase]  # AFN generado por cada terminal
    dfa: Dict[str, AutomatonBase]  # AFD generado por cada terminal