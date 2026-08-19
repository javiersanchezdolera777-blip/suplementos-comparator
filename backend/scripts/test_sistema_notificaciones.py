import sys
import os
from dotenv import load_dotenv

# Cargamos el .env local del backend
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

# Añadimos el directorio backend al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("🔍 [1/4] Verificando variables de entorno...")
print(f"   - DATABASE_URL configurada: {'Sí ✅' if os.getenv('DATABASE_URL') else 'No ❌'}")
print(f"   - RESEND_API_KEY configurada: {'Sí ✅' if os.getenv('RESEND_API_KEY') else 'No ❌'}")
print(f"   - FRONTEND_URL: {os.getenv('FRONTEND_URL', 'No definida (usará fallback de producción)')}")

from services.email_service import enviar_email_bienvenida, enviar_resumen_alertas_favoritos, enviar_newsletter_suscripcion

def test_correos():
    correo_prueba = "javiersanchezdolera9@gmail.com" # O el tuyo personal para pruebas
    print(f"\n📧 [2/4] Probando envío de Correo de Bienvenida a '{correo_prueba}'...")
    try:
        enviar_email_bienvenida(correo_prueba)
        print("   -> ¡Función de bienvenida ejecutada! Revisa tus logs de Resend.")
    except Exception as e:
        print(f"   -> ❌ Falló la prueba de bienvenida: {e}")

    print(f"\n🔥 [3/4] Probando envío de Alerta de Favoritos (Resumen simulado)...")
    try:
        productos_falsos = [
            {"nombre": "Proteína Whey Test 1kg", "precio_viejo": 35.0, "precio_nuevo": 27.5, "slug": "proteina-whey-test"}
        ]
        enviar_resumen_alertas_favoritos(correo_prueba, productos_falsos)
        print("   -> ¡Función de resumen de favoritos ejecutada!")
    except Exception as e:
        print(f"   -> ❌ Falló la prueba de favoritos: {e}")

    print(f"\n📬 [4/4] Probando envío de Newsletter simulada...")
    try:
        html_prueba = "<h2>Prueba de Newsletter</h2><p>Este es un test local del sistema refactorizado.</p>"
        enviar_newsletter_suscripcion(correo_prueba, html_prueba)
        print("   -> ¡Función de newsletter ejecutada!")
    except Exception as e:
        print(f"   -> ❌ Falló la prueba de newsletter: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO TEST LOCAL DE SUBSISTEMAS DE NOTIFICACIÓN\n" + "-"*50)
    test_correos()
    print("\n" + "-"*50 + "\n🏁 Pruebas finalizadas. Comprueba tu panel de Resend y tu bandeja de entrada.")