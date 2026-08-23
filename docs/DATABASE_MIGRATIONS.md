# Cheat Sheet: Migraciones con Alembic

Esta guía rápida sirve para el equipo de desarrollo a la hora de modificar la estructura de la base de datos de "Tus Suplementos".

## Flujo de Trabajo Básico

Cada vez que añadas, elimines o modifiques una columna en `backend/models.py`, **NUNCA** debes aplicar los cambios directamente en producción. Sigue estos pasos:

### 1. Generar la Migración
Asegúrate de estar en el directorio `backend` y ejecuta:
```bash
alembic revision --autogenerate -m "Añadida columna X a la tabla Y"
```
*Esto analizará la diferencia entre tus `models.py` y la base de datos actual, generando un archivo Python en la carpeta `alembic/versions/`.*

### 2. Revisar la Migración (Obligatorio)
Abre el archivo generado en `alembic/versions/` y comprueba visualmente que las funciones `upgrade()` y `downgrade()` hacen exactamente lo que esperas. ¡Alembic no es infalible!

### 3. Aplicar los Cambios a la Base de Datos
Una vez verificada, empuja los cambios a Neon DB ejecutando:
```bash
alembic upgrade head
```
*El parámetro `head` le indica a Alembic que aplique todas las migraciones pendientes hasta llegar a la última versión.*

---

## Comandos de Emergencia

- **Retroceder una migración (Downgrade):**
  Si te has equivocado y necesitas deshacer el último `upgrade`, ejecuta:
  ```bash
  alembic downgrade -1
  ```
- **Ver el historial de migraciones:**
  ```bash
  alembic history --verbose
  ```
- **Saber en qué versión está la base de datos actualmente:**
  ```bash
  alembic current
  ```
