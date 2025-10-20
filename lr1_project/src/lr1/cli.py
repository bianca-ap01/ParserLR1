
from __future__ import annotations
import argparse, json, sys
from .grammar_io import load_grammar_file
from .builder import LR1Builder
from .tables import Tables
from .parser import Parser
from .lexer import Lexer

def _build_tables(grammar_path: str):
    spec, G = load_grammar_file(grammar_path)
    builder = LR1Builder(G)
    states, trans = builder.build_canonical_collection()
    tables = Tables(G, states, trans, builder.aug_start)
    return spec, G, builder, tables

def cmd_build(args):
    spec, G, builder, tables = _build_tables(args.grammar)
    if args.tables:
        print(tables.dump_tables())
        print()
    if args.conflicts:
        print(tables.dump_conflicts())

def cmd_parse(args):
    spec, G, builder, tables = _build_tables(args.grammar)
    L = Lexer(spec.lex_rules)
    with open(args.input, 'r', encoding='utf-8') as f:
        program = f.read()
    tokens = L.tokenize(program)
    P = Parser(tables, build_tree=args.tree)
    try:
        root = P.parse(tokens if not args.justtypes else [t for (t, lx) in tokens])
        if args.envelope:
            print(json.dumps({
                'ok': True, 'message': 'Parseo exitoso',
                'conflicts': [
                    {'type': c[0], 'state': c[1], 'symbol': c[2]}
                    for c in tables.conflicts
                ],
                'ast': (root.pretty() if root else None)
            }, ensure_ascii=False))
        else:
            print('Parseo exitoso')
            if args.tree and root:
                print('\nÁrbol:')
                print(root.pretty())
    except Exception as e:
        if args.envelope:
            print(json.dumps({'ok': False, 'message': str(e)}, ensure_ascii=False))
        else:
            print('ERROR:', e, file=sys.stderr)
            sys.exit(1)

def main(argv=None):
    p = argparse.ArgumentParser(prog='lr1', description='LR(1) labs-style')
    sub = p.add_subparsers(dest='cmd', required=True)

    b = sub.add_parser('build', help='Construir tablas LR(1) y mostrarlas')
    b.add_argument('grammar')
    b.add_argument('--tables', action='store_true')
    b.add_argument('--conflicts', action='store_true')
    b.set_defaults(func=cmd_build)

    r = sub.add_parser('parse', help='Parsear un input con la gramática dada')
    r.add_argument('grammar')
    r.add_argument('input')
    r.add_argument('--tree', action='store_true')
    r.add_argument('--envelope', action='store_true')
    r.add_argument('--justtypes', action='store_true', help='Usar sólo tipos de token')
    r.set_defaults(func=cmd_parse)

    args = p.parse_args(argv)
    args.func(args)

if __name__ == '__main__':
    main()