import subprocess
import sys
import os


def run_script(script_name, relative_path):
    # Calcula la ruta absoluta del script a ejecutar
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script_path = os.path.join(base_dir, relative_path)

    print(f"\n{'='*60}")
    print(f"🚀 EJECUTANDO: {script_name}")
    print(f"{'='*60}")

    try:
        # subprocess simula la ejecución en una terminal independiente (igual que GitHub Actions)
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=False,  # Permite que los prints originales salgan en tu consola en tiempo real
        )
        print(f"\n✅ {script_name} finalizó con éxito (Exit Code: 0)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERROR FATAL en {script_name} (Exit Code: {e.returncode})")
        return False


def master_monitor():
    print("🔍 INICIANDO AUDITORÍA GLOBAL DE CRONS...\n")

    # Definimos la batería de los 4 procesos clave
    scripts = [
        ("1. Pipeline de Precios", "actualizador_precios.py"),
        ("2. Publicador Telegram (Deals)", "send_telegram_deals.py"),
        ("3. Newsletter Top 5", "newsletter_semanal.py"),
        ("4. Retargeting Automatizado", "retargeting_vistas.py"),
    ]

    fallos = 0

    for nombre, ruta in scripts:
        if not run_script(nombre, ruta):
            fallos += 1

    print(f"\n{'*'*60}")
    print("🏁 DIAGNÓSTICO FINAL DEL SISTEMA")
    if fallos == 0:
        print(
            "🟢 ESTADO: PERFECTO. Los 4 CRONs ejecutaron sin errores de sistema ni excepciones."
        )
    else:
        print(
            f"🔴 ESTADO: ALERTA. {fallos} CRON(s) fallaron y detuvieron su ejecución. Revisa las trazas arriba."
        )
    print(f"{'*'*60}\n")


if __name__ == "__main__":
    master_monitor()
