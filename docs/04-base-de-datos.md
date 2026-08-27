# 5. BASE DE DATOS

## Tecnologías Principales
*   **Motor:** PostgreSQL.
*   **Proveedor Cloud:** Neon DB (Serverless Postgres).
*   **Gestor ORM:** SQLAlchemy (v2) a través de `database.py`.
*   **Migraciones:** Actualmente se usa `Base.metadata.create_all(bind=engine)`, aunque está prevista la migración a Alembic en el *roadmap* para la V2 Multi-Tienda.

## Estructura y Entidades Principales
La base de datos sigue un modelo relacional puro, normalizado para las entidades principales pero permitiendo cierta flexibilidad con columnas JSON para arrays complejos como `sabor` y `objetivo`.

### 1. Entidades del Catálogo (Core)

#### `Producto` (Tabla `productos`)
El corazón del sistema. Cada producto es una oferta única atada a una tienda.
*   **Campos clave:** `nombre`, `precio` (float), `precio_anterior` (float), `imagen_url`, `afiliado_url`, `tienda` (string).
*   **Métricas derivadas:** `peso_gramos`, `precio_por_kg`.
*   **Clasificación NLP:** `formato`, `es_vegano`, `sin_gluten`, `sin_lactosa`, `tipo_proteina`, `porcentaje_proteina`...
*   **Campos operativos:** `clics_count` (para relevancia), `publicado_telegram`, `fecha_publicacion_telegram` (para el sistema de cooldown de avisos).
*   **Relaciones:** Pertenece a una `Marca` (N:1) y a una `Categoria` (N:1). Tiene 1:N `resenas`.

#### `Marca` (Tabla `marcas`)
Entidad maestra para agrupar variantes.
*   **Campos clave:** `nombre` (Único).

#### `Categoria` (Tabla `categorias`)
Taxonomía rígida generada por el Cerebro NLP.
*   **Campos clave:** `nombre` (Único).

### 2. Entidades de Autenticación y Privacidad

#### `Usuario` (Tabla `usuarios`)
La capa de identidad privada.
*   **Campos clave:** `email` (Único), `hashed_password`.
*   **Relaciones:** 1:N `favoritos`, 1:N `historial_vistas`. Relación 1:1 estricta con `Perfil` (el cual es público).

### 3. Entidades de la Comunidad (Gamificación)

Esta es la nueva capa "Social" del proyecto, implementada recientemente.

#### `Perfil` (Tabla `perfiles`)
El "escaparate público" del usuario. Aisla los datos sensibles.
*   **Campos clave:** `username` (Único, tipo Instagram), `avatar_url`, `bio`, `suplemento_favorito`, `puntos_totales`, `racha_actual`, `objetivo_etapa`.
*   **Relaciones:** Pertenece a un `Usuario` (1:1). Tiene 1:N `stacks`, 1:N `resenas`, 1:N `checkins`.
*   **Seguidores:** Relación M:M consigo misma a través de la tabla puente `seguidores`.

#### `Stack` (Tabla `stacks`)
"Listas de reproducción" de suplementos (ej. "Definición 2026").
*   **Campos clave:** `nombre`, `descripcion`, `es_publico`.
*   **Relaciones:** Creado por un `Perfil`. Contiene múltiples `Productos` mediante la tabla puente `stack_producto`.

#### `CheckDiario` (Tabla `checks_diarios`)
Registro del hábito de suplementación (Gamificación).
*   **Campos clave:** `fecha` (Date, clave para verificar que se hizo "hoy"), `puntos_ganados`.
*   **Relaciones:** Pertenece a un `Perfil`.

#### `ResenaSabor` (Tabla `resenas_sabores`)
*   **Campos clave:** `sabor_probado`, `nota`, `comentario`.
*   **Relaciones:** Une a un `Perfil` y a un `Producto`.

## Diagrama de Relaciones

```text
Usuario 1──────1 Perfil
  │                 │
  │                 ├───1:N────> CheckDiario
  │                 ├───M:N────> Perfil (Seguidores)
  ├──1:N──> Favorito│
  ├──1:N──> Historial           ├───1:N────> ResenaSabor ◄────┐
  │                 │           │                             │
  │                 └───1:N────> Stack ───M:N──┐              │
  │                                            ▼              │
  └───────────────────────────────────────> Producto ◄──1:N───┘
                                               │
                                               ├──N:1──> Marca
                                               └──N:1──> Categoria
```

## Patrones de Acceso e Índices
*   La entidad `Producto` tiene un alto volumen de lecturas. Se han añadido índices en `slug`, `nombre`, `sin_gluten` y `sin_lactosa` para acelerar los filtros cruzados.
*   El backend usa transacciones y dependencias de SQLAlchemy (`Yield db`) para asegurar la limpieza de conexiones.
*   El diseño actual asocia 1 producto = 1 tienda + 1 precio. Esto permite un catálogo veloz pero limita comparar la variación de un idéntico SKU en varias tiendas (el roadmap prevé un refactor a modelo Relacional Multi-tienda V2).
