import sys
import os
from dotenv import load_dotenv

# Cargar entorno del backend
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("🔍 Verificando entorno para las pruebas...")
if not os.getenv("RESEND_API_KEY"):
    print("❌ ERROR: Falta RESEND_API_KEY en el .env")
    sys.exit(1)

from services.email_service import (
    enviar_email_bienvenida,
    enviar_alerta_bajada_precio,
    enviar_resumen_alertas_favoritos,
)


def ejecutar_bateria_pruebas():
    correo_destino = "javiersanchezdolera9@gmail.com"
    print(
        f"\n🚀 DISPARANDO BATERÍA DE PRUEBAS DE EMAIL A: {correo_destino}\n" + "-" * 50
    )

    # 1. Test Correo de Bienvenida (Nuevo diseño corporativo limpio)
    print("📧 [1/3] Enviando correo de bienvenida...")
    try:
        enviar_email_bienvenida(correo_destino)
        print("   ✅ Bienvenida enviada con éxito.")
    except Exception as e:
        print(f"   ❌ Error en bienvenida: {e}")

    # 2. Test Alerta de Bajada Individual con Imagen
    print("\n🔥 [2/3] Enviando alerta de bajada de precio individual...")
    try:
        enviar_alerta_bajada_precio(
            email=correo_destino,
            nombre_producto="Iso Whey Zero 2kg - BiotechUSA",
            precio_viejo=54.99,
            precio_nuevo=39.99,
            slug="iso-whey-zero-2kg",
            imagen_url="https://www.tussuplementos.com/Logo_icon2.png",  # Usamos el logo temporalmente como miniatura de prueba
        )
        print("   ✅ Alerta individual enviada con éxito.")
    except Exception as e:
        print(f"   ❌ Error en alerta individual: {e}")

    # 3. Test Resumen de Favoritos (Múltiples productos)
    print("\n🎯 [3/3] Enviando resumen de favoritos (múltiples bajadas)...", flush=True)
    try:
        favoritos_rebajados = [
            {
                "nombre": "Monohidrato de Creatina Pura 500g",
                "precio_viejo": 24.95,
                "precio_nuevo": 18.95,
                "slug": "creatina-monohidrato-500g",
            },
            {
                "nombre": "Proteína Whey Concentrada 1kg",
                "precio_viejo": 32.00,
                "precio_nuevo": 24.50,
                "slug": "whey-concentrada-1kg",
            },
        ]
        enviar_resumen_alertas_favoritos(correo_destino, favoritos_rebajados)
        print("   ✅ Resumen de favoritos enviado con éxito.")
    except Exception as e:
        print(f"   ❌ Error en resumen de favoritos: {e}")

    print(
        "\n"
        + "-" * 50
        + "\n🏁 Pruebas terminadas. Revisa tu bandeja de entrada y el panel de Resend."
    )


if __name__ == "__main__":
    ejecutar_bateria_pruebas()
