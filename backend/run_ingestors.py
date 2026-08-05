import os
import sys
import subprocess
import time

ROOT = os.path.dirname(os.path.abspath(__file__))

INGESTORS = [
    [sys.executable, os.path.join(ROOT, "ingestores", "sportlive.py")],
    [sys.executable, os.path.join(ROOT, "ingestores", "pharma2go.py")],
    [sys.executable, os.path.join(ROOT, "ingestores", "hsn.py")],
]

for script in INGESTORS:
    print(f"\n▶ Ejecutando {os.path.basename(script[1])}...")
    subprocess.run(script, cwd=ROOT, check=False)
    time.sleep(5)

print("\n✅ Ejecución secuencial completada.")
