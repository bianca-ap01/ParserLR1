from lr1.grammar_io import load_grammar_file

spec, G = load_grammar_file('grammar/expr.txt')
print('START:', spec.start)
print('NONTERMINALS:', spec.nonterms)
print('TERMINALS:', spec.terms)
print('\nFIRST sets:')
for X in sorted(list(G.terminals | G.nonterminals)):
    print(f"FIRST({X}) = {sorted(G.first(X))}")

print('\nFOLLOW sets:')
for A, S in sorted(G.follow_sets().items()):
    print(f"FOLLOW({A}) = {sorted(S)}")
