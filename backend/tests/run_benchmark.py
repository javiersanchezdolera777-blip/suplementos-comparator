import os
import sys
import time
import tracemalloc
from urllib.parse import urlparse
from fastapi.testclient import TestClient

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
for ruta in (BACKEND_DIR, TESTS_DIR):
    if ruta not in sys.path:
        sys.path.insert(0, ruta)

import main
import seed_data
import legacy_productos
from sqlalchemy import event

main.app.include_router(legacy_productos.router)

def run_benchmark(n_productos=1000):
    print(f"\n=======================================================")
    print(f"BENCHMARK /api/productos: ANTIGUO vs NUEVO (N={n_productos} productos)")
    print(f"=======================================================")
    seed_data.seed(main.engine, n_productos=n_productos, seed_value=42)
    
    client = TestClient(main.app)
    
    class QueryCounter:
        def __init__(self, engine):
            self.engine = engine
            self.count = 0
            self.rows = 0
        def _after(self, conn, cursor, statement, parameters, context, executemany):
            self.count += 1
            if cursor.rowcount > 0:
                self.rows += cursor.rowcount
        def __enter__(self):
            event.listen(self.engine, "after_cursor_execute", self._after)
            return self
        def __exit__(self, *exc):
            event.remove(self.engine, "after_cursor_execute", self._after)

    escenarios = [
        ("Página 1 (sin filtros)", {"limit": 36, "page": 1}),
        ("Página 10 (sin filtros)", {"limit": 36, "page": 10}),
        ("Filtro Sabor + Precio ASC (pág 1)", {"sabor": "chocolate", "orden": "precio_asc", "limit": 36, "page": 1}),
        ("Filtro Categ + Descuento (pág 1)", {"categoria": "Proteínas", "orden": "descuento", "limit": 36, "page": 1}),
        ("Solo Ofertas + Precio DESC (pág 1)", {"solo_ofertas": "true", "orden": "precio_desc", "limit": 36, "page": 1}),
    ]
    
    for nombre, params in escenarios:
        print(f"\n--- Escenario: {nombre} ---")
        
        # 1. ANTIGUO
        tracemalloc.start()
        t0 = time.perf_counter()
        with QueryCounter(main.engine) as qc_old:
            res_old = client.get("/legacy/api/productos", params=params)
        t_old = (time.perf_counter() - t0) * 1000
        mem_old_curr, mem_old_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        assert res_old.status_code == 200
        total_old = res_old.json()["total_resultados"]
        
        # 2. NUEVO
        tracemalloc.start()
        t0 = time.perf_counter()
        with QueryCounter(main.engine) as qc_new:
            res_new = client.get("/api/productos", params=params)
        t_new = (time.perf_counter() - t0) * 1000
        mem_new_curr, mem_new_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        assert res_new.status_code == 200
        total_new = res_new.json()["total_resultados"]
        assert total_new == total_old
        
        print(f"Total productos coincidentes: {total_new}")
        print(f"  [ANTIGUO] Tiempo: {t_old:6.2f} ms | Queries: {qc_old.count:2d} | Filas DB: {qc_old.rows:5d} | Pico RAM: {mem_old_peak/1024:6.1f} KB")
        print(f"  [NUEVO]   Tiempo: {t_new:6.2f} ms | Queries: {qc_new.count:2d} | Filas DB: {qc_new.rows:5d} | Pico RAM: {mem_new_peak/1024:6.1f} KB")
        if t_new < t_old:
            mejora_t = ((t_old - t_new) / t_old) * 100
            print(f"  >>> Mejora tiempo: {mejora_t:.1f}% más rápido")
        if qc_new.rows < qc_old.rows:
            reduc_filas = ((qc_old.rows - qc_new.rows) / qc_old.rows) * 100
            print(f"  >>> Reducción filas intermedias transferidas: {reduc_filas:.1f}%")

if __name__ == "__main__":
    run_benchmark(n_productos=1000)
