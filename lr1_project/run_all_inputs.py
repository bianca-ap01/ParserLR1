
import os, subprocess, sys

BASE = os.path.dirname(os.path.abspath(__file__))
GRAMMAR = os.path.join(BASE, 'grammar', 'expr.txt')
INPUT_DIR = os.path.join(BASE, 'inputs')
OUTPUT_DIR = os.path.join(BASE, 'outputs')

os.makedirs(OUTPUT_DIR, exist_ok=True)

for name in sorted(os.listdir(INPUT_DIR)):
    if not name.startswith('input') or not name.endswith('.txt'):
        continue
    in_path = os.path.join(INPUT_DIR, name)
    out_path = os.path.join(OUTPUT_DIR, name.replace('input', 'output'))
    print(f"Ejecutando {name}")
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'lr1.cli', 'parse', GRAMMAR, in_path, '--tree', '--envelope'],
            capture_output=True, text=True, cwd=BASE, timeout=30,
        )
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write("=== STDOUT ===\n")
            f.write(result.stdout)
            f.write("\n\n=== STDERR ===\n")
            f.write(result.stderr)
    except Exception as e:
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write("ERROR: " + str(e))