import sys
import requests

# ⚠️ REEMPLAZA ESTO CON TUS DATOS REALES ANTES DE EJECUTAR
TOKEN = "8930459674:AAHVOnI4qXeJRRdEwIAH-PDwh4NGUaOiu4s"
CHAT_ID = "@TusSuplementosChollos" # Recuerda que los canales de Telegram suelen empezar por -100

print("🔍 INICIANDO DIAGNÓSTICO...")

print("\n📡 1. Probando API de Telegram pura...")
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": "🚀 *Test de diagnóstico* completado con éxito.",
    "parse_mode": "Markdown"
}

try:
    res = requests.post(url, json=payload).json()
    if res.get("ok"):
        print("✅ ÉXITO: El bot tiene permisos y el mensaje ha llegado al canal.")
    else:
        print(f"❌ FALLO TELEGRAM: {res.get('description')}")
except Exception as e:
    print(f"❌ FALLO HTTP: {e}")

print("\n🗄️ 2. Probando Base de Datos (Chollos pendientes)...")
try:
    sys.path.append('backend')
    from database import SessionLocal
    import models

    db = SessionLocal()
    pendientes = db.query(models.Producto).filter(
        models.Producto.precio_anterior.isnot(None),
        models.Producto.precio < models.Producto.precio_anterior,
        models.Producto.publicado_telegram == False
    ).count()

    print(f"📊 Productos listos para publicar encontrados: {pendientes}")
    if pendientes == 0:
        print("⚠️ AVISO: El script en GitHub no publica nada porque la base de datos no tiene chollos pendientes.")
    db.close()
except Exception as e:
    print(f"❌ FALLO DB: {e}")
