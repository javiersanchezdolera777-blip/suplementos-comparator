"""
Script de Sanitización de Historial de Precios
===============================================
Elimina registros redundantes de la tabla `precios_historicos` donde el precio
es idéntico (con redondeo a 2 decimales) al del registro cronológico inmediatamente
anterior para la misma oferta_id.

Uso:
    cd backend
    python scripts/limpiar_historicos_duplicados.py

    Flags:
        --dry-run   (por defecto) Solo analiza y reporta, NO borra nada.
        --execute   Ejecuta la purga real en la base de datos.
"""

import sys
import os

# Aseguramos que el directorio raíz del backend esté en el PATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import text
from database import SessionLocal


def limpiar_historicos(execute: bool = False):
    db = SessionLocal()

    try:
        # 1. Obtener todas las oferta_id que tienen registros históricos
        ofertas = db.execute(
            text("SELECT DISTINCT oferta_id FROM precios_historicos ORDER BY oferta_id")
        ).fetchall()

        total_ofertas = len(ofertas)
        total_registros_analizados = 0
        total_duplicados = 0
        ids_a_borrar = []

        print(f"🔍 Analizando historial de precios para {total_ofertas} ofertas...\n")

        for (oferta_id,) in ofertas:
            # 2. Para cada oferta, obtener sus registros ordenados cronológicamente
            registros = db.execute(
                text("""
                    SELECT id, precio, fecha
                    FROM precios_historicos
                    WHERE oferta_id = :oferta_id
                    ORDER BY fecha ASC, id ASC
                """),
                {"oferta_id": oferta_id}
            ).fetchall()

            total_registros_analizados += len(registros)

            if len(registros) <= 1:
                continue  # Nada que comparar si solo hay 0 o 1 registro

            # 3. Comparar cada registro con el anterior usando round(..., 2)
            precio_anterior_redondeado = round(registros[0][1], 2)

            for i in range(1, len(registros)):
                reg_id = registros[i][0]
                precio_actual_redondeado = round(registros[i][1], 2)

                if precio_actual_redondeado == precio_anterior_redondeado:
                    # Este registro es redundante: mismo precio que el anterior
                    ids_a_borrar.append(reg_id)
                    total_duplicados += 1
                else:
                    # Precio diferente: este registro es legítimo
                    precio_anterior_redondeado = precio_actual_redondeado

        # 4. Reporte
        print("=" * 60)
        print(f"📊 INFORME DE SANITIZACIÓN")
        print("=" * 60)
        print(f"   Ofertas analizadas:        {total_ofertas}")
        print(f"   Registros totales:         {total_registros_analizados}")
        print(f"   Duplicados detectados:     {total_duplicados}")
        print(f"   Registros legítimos:       {total_registros_analizados - total_duplicados}")
        print(f"   Ratio de basura:           {(total_duplicados / max(total_registros_analizados, 1) * 100):.1f}%")
        print("=" * 60)

        if not ids_a_borrar:
            print("\n✅ ¡La tabla está limpia! No hay duplicados que purgar.")
            return

        if execute:
            print(f"\n🗑️  Ejecutando purga de {len(ids_a_borrar)} registros redundantes...")

            # Borrar en lotes de 500 para no saturar la BD
            batch_size = 500
            for i in range(0, len(ids_a_borrar), batch_size):
                batch = ids_a_borrar[i:i + batch_size]
                placeholders = ", ".join([str(id_) for id_ in batch])
                db.execute(
                    text(f"DELETE FROM precios_historicos WHERE id IN ({placeholders})")
                )
                db.commit()
                print(f"   ✅ Lote {i // batch_size + 1}: {len(batch)} registros eliminados")

            print(f"\n🎉 ¡Purga completada! Se eliminaron {len(ids_a_borrar)} registros fantasma.")
        else:
            print(f"\n⚠️  MODO DRY-RUN: No se ha borrado nada.")
            print(f"   Para ejecutar la purga real, usa: python scripts/limpiar_historicos_duplicados.py --execute")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error durante la sanitización: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    modo_execute = "--execute" in sys.argv
    if modo_execute:
        print("🔴 MODO EJECUCIÓN REAL — Los registros se borrarán de la base de datos.\n")
    else:
        print("🟡 MODO DRY-RUN — Solo análisis, sin borrar nada.\n")

    limpiar_historicos(execute=modo_execute)
