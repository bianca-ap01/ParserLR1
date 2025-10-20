
# LR(1) Compiler — Labs Style

Includes:
- Grammar loader from text file (START/NONTERMINALS/TERMINALS/PRODUCTIONS/LEXER)
- Canonical LR(1) construction: closure/goto + canonical collection
- ACTION/GOTO tables with conflict detection
- Table-driven parser with optional AST
- Simple regex-based lexer
- CLI with `build` and `parse`
- `run_all_inputs.py` to iterate inputs and dump outputs (JSON envelope ready)

## Install (editable)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ./src
```

## Quick use
```bash
python -m lr1.cli build grammar/expr.txt --tables --conflicts
python -m lr1.cli parse grammar/expr.txt inputs/input1.txt --tree --envelope
python run_all_inputs.py
```