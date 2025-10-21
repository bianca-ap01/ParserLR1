from lr1.grammar_io import GrammarSpec, load_grammar_file
from lr1.grammar import Grammar

text = """
S' -> E
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
"""

# Use the loader that accepts plain BNF
spec = GrammarSpec()
# emulate what load_grammar_file would infer
spec.prods = []
for ln in [l.strip() for l in text.strip().splitlines() if l.strip()]:
    if '->' not in ln:
        continue
    lhs, rhs = ln.split('->',1)
    A = lhs.strip()
    alts = [alt.strip() for alt in rhs.split('|')]
    for alt in alts:
        if alt == '' or alt.lower() == 'ε':
            spec.prods.append((A, []))
        else:
            symbols = [s for s in alt.split() if s]
            spec.prods.append((A, symbols))

# Infer start/nonterms/terms
lhs_order = [A for (A,_) in spec.prods]
spec.start = lhs_order[0]
nonterms = {A for (A,_) in spec.prods}
spec.nonterms = sorted(list(nonterms))
rhs_syms = set()
for (_, rhs) in spec.prods:
    for s in rhs:
        if s != 'ε':
            rhs_syms.add(s)
spec.terms = sorted([s for s in rhs_syms if s not in nonterms])


# Mostrar solo los no terminales definidos por el usuario (LHS de las producciones)
user_nonterms = sorted({A for (A, _) in spec.prods})
print('Spec start:', spec.start)
print('Nonterms (solo usuario):', user_nonterms)
print('Terms:', spec.terms)

G = spec.to_grammar()
print('Productions:')
for p in G.productions:
    print(p)

try:
    print('\nComputing FIRST for terminales y no terminales del usuario...')
    for X in sorted(user_nonterms + spec.terms):
        print('FIRST({}) = {}'.format(X, sorted(G.first(X))))
    print('\nComputing FOLLOW sets (solo usuario)...')
    for A in user_nonterms:
        S = G.follow_sets().get(A, set())
        print('FOLLOW({}) = {}'.format(A, sorted(S)))
except Exception as e:
    import traceback
    traceback.print_exc()
    print('Exception type:', type(e))
