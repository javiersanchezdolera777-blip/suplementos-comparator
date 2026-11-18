"""ORÁCULO DE PARIDAD — NO USAR EN PRODUCCIÓN.

Copia literal de obtener_productos() tal y como estaba en main@a5cf0a9
(antes de la paginación en base de datos). Solo cambian el decorador
(se monta en un APIRouter de pruebas bajo /legacy/api/productos) y el nombre
de la función. Se usa exclusivamente en los tests para comparar la
implementación antigua con la nueva sobre la misma base de datos de pruebas.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, nulls_last, or_
from sqlalchemy.orm import Session, selectinload

import models
import schemas
from busqueda import expandir_terminos_busqueda
from main import get_db

router = APIRouter()

@router.get("/legacy/api/productos", response_model=schemas.PaginatedProducts)
def obtener_productos_legacy(
    request: Request,
    skip: int = 0,
    # Soportamos tanto el parámetro antiguo (singular) como el de
    # multiselección (plural)
    categoria: Optional[str] = None,
    categorias: Optional[str] = Query(None),
    marca: Optional[str] = None,
    marcas: Optional[str] = Query(None),
    objetivo: Optional[str] = None,
    objetivos: Optional[str] = Query(None),
    sabor: Optional[str] = None,
    sabores: Optional[str] = Query(None),
    formato: Optional[str] = None,
    formatos: Optional[str] = Query(None),
    es_vegano: Optional[bool] = None,
    sin_gluten: Optional[bool] = Query(None),
    sin_lactosa: Optional[bool] = Query(None),
    sello_calidad: Optional[str] = None,
    tipo_proteina: Optional[str] = None,
    tipo_creatina: Optional[str] = None,
    perfil_aminoacidos: Optional[str] = None,
    tipo_vitamina: Optional[str] = None,
    busqueda: Optional[str] = None,
    q: Optional[str] = Query(None, description="Alias de búsqueda"),
    db: Session = Depends(get_db),
    porcentaje_proteina: Optional[int] = Query(
        None, description="Filtra por porcentaje de proteína (ej. 80)"
    ),
    solo_ofertas: Optional[bool] = Query(
        False, description="Muestra solo productos con descuento real"
    ),
    orden: str = Query(
        "relevancia",
        description="Orden de resultados: relevancia, precio_asc, precio_desc, descuento",
    ),
    page: int = Query(1, ge=1),
    limit: int = Query(100, le=200),
):
    # 0. Evaluar si necesitamos cruzar con Ofertas (solo si hay orden por precio o filtro solo_ofertas)
    sort_final = (
        request.query_params.get("orden_precio")
        or request.query_params.get("ordenar_por")
        or request.query_params.get("sort")
        or orden
    )
    
    necesita_join_ofertas = solo_ofertas or sort_final in [
        "precio_asc", "price_asc", "asc", 
        "precio_desc", "price_desc", "desc", 
        "descuento"
    ]

    # Join inicial maestro optimizado
    query = (
        db.query(models.Producto)
        .join(models.Categoria, isouter=True)
        .join(models.Marca, isouter=True)
    )
    
    if necesita_join_ofertas:
        query = query.outerjoin(models.Oferta)

    # 1. Filtros de Categoría
    cat_str = categorias or categoria
    if cat_str and cat_str.lower() != "todos":
        lista_cats = [c.strip() for c in cat_str.split(",") if c.strip()]
        if lista_cats:
            query = query.filter(models.Categoria.nombre.in_(lista_cats))

    # 2. Filtros de Marca
    marca_str = marcas or marca
    if marca_str:
        lista_marcas_lower = [
            m.strip().lower() for m in marca_str.split(",") if m.strip()
        ]
        if lista_marcas_lower:
            query = query.filter(
                func.lower(models.Marca.nombre).in_(lista_marcas_lower)
            )

    # 3. Filtro Porcentaje Proteína
    if porcentaje_proteina is not None:
        query = query.filter(
            models.Producto.porcentaje_proteina >= porcentaje_proteina)

    # 4. Filtros Básicos (Formatos, Vegano, Sellos)
    formato_str = formatos or formato
    if formato_str:
        lista_formatos = [f.strip()
                          for f in formato_str.split(",") if f.strip()]
        if lista_formatos:
            query = query.filter(models.Producto.formato.in_(lista_formatos))

    if es_vegano is not None:
        query = query.filter(models.Producto.es_vegano == es_vegano)
    if sin_gluten is True:
        query = query.filter(models.Producto.sin_gluten.is_(True))
    if sin_lactosa is True:
        query = query.filter(models.Producto.sin_lactosa.is_(True))

    if solo_ofertas:
        # Ahora el cálculo del descuento tira de models.Oferta
        descuento_pct = (
            (models.Oferta.precio_anterior - models.Oferta.precio)
            / models.Oferta.precio_anterior
        ) * 100

        query = query.filter(
            models.Oferta.precio_anterior.isnot(None),
            models.Oferta.precio_anterior > models.Oferta.precio,
            models.Oferta.precio_anterior > 0,
            or_(
                (models.Categoria.nombre.in_(["Proteínas", "Creatinas"]))
                & (descuento_pct >= 30),
                (models.Categoria.nombre.in_(["Aminoácidos", "Pre-Entrenos"]))
                & (descuento_pct >= 40),
                (
                    ~models.Categoria.nombre.in_(
                        ["Proteínas", "Creatinas", "Aminoácidos", "Pre-Entrenos"]
                    )
                )
                & (descuento_pct >= 50),
            ),
        )

    if sello_calidad:
        query = query.filter(
            models.Producto.sello_calidad.ilike(
                f"%{sello_calidad}%"))

    # 5. Sub-filtros
    if tipo_proteina:
        query = query.filter(
            models.Producto.tipo_proteina.ilike(
                f"%{tipo_proteina}%"))
    if tipo_creatina:
        query = query.filter(
            models.Producto.tipo_creatina.ilike(
                f"%{tipo_creatina}%"))
    if perfil_aminoacidos:
        query = query.filter(
            models.Producto.perfil_aminoacidos.ilike(f"%{perfil_aminoacidos}%")
        )
    if tipo_vitamina:
        query = query.filter(
            models.Producto.tipo_vitamina.ilike(
                f"%{tipo_vitamina}%"))

    # 6. Buscador de texto libre con Expansión Semántica
    busqueda_final = busqueda or q
    if busqueda_final:
        grupos_tokens = expandir_terminos_busqueda(busqueda_final)
        for grupo in grupos_tokens:
            condiciones_token = []
            for term in grupo:
                patron = f"%{term}%"
                condiciones_token.append(models.Producto.nombre.ilike(patron))
                condiciones_token.append(models.Marca.nombre.ilike(patron))
                condiciones_token.append(models.Categoria.nombre.ilike(patron))
            query = query.filter(or_(*condiciones_token))

    # ... (deja igual los subfiltros y buscador de texto libre) ...

    # 7. ORDENACIÓN (Ahora tira de Oferta)


    if sort_final in ["precio_asc", "price_asc", "asc"]:
        query = query.order_by(models.Oferta.precio.asc())
    elif sort_final in ["precio_desc", "price_desc", "desc"]:
        query = query.order_by(models.Oferta.precio.desc())
    elif sort_final == "descuento":
        query = query.order_by(
            (models.Oferta.precio_anterior - models.Oferta.precio).desc()
        )
    else:
        # ORDEN POR DEFECTO: RELEVANCIA INTELIGENTE
        if busqueda_final:
            text_score = func.similarity(
                models.Producto.nombre,
                busqueda_final).label("text_score")
            query = query.order_by(
                text_score.desc(),
                nulls_last(models.Producto.clics_count.desc()),
                models.Producto.id.asc(),
            )
        else:
            query = query.order_by(
                nulls_last(models.Producto.clics_count.desc()),
                models.Producto.id.asc(),
            )

    # 8. Extraer y filtrar Sabores y Objetivos (Arrays Multiselección)
    # ESTRATEGIA OPTIMIZADA: Solo pedimos a SQL los campos mínimos para filtrar y ordenar (IDs, sabor, objetivo)
    
    # Extraemos solo las tuplas ligeras manteniendo el orden de la query original
    datos_raw_duplicados = query.with_entities(
        models.Producto.id, 
        models.Producto.sabor, 
        models.Producto.objetivo
    ).all()

    datos_raw = []
    vistos = set()
    for row in datos_raw_duplicados:
        if row.id not in vistos:
            vistos.add(row.id)
            datos_raw.append(row)

    sabor_str = sabores or sabor
    sabores_lista = (
        [s.strip().lower() for s in sabor_str.split(",") if s.strip()]
        if sabor_str
        else []
    )

    objetivo_str = objetivos or objetivo
    objetivos_lista = (
        [o.strip().lower() for o in objetivo_str.split(",") if o.strip()]
        if objetivo_str
        else []
    )

    def cumple_filtros_arrays(fila):
        # ¿Cumple el sabor?
        if sabores_lista:
            valor_sabor = fila.sabor
            if isinstance(valor_sabor, list):
                if not any(str(item).lower() in sabores_lista for item in valor_sabor):
                    return False
            elif isinstance(valor_sabor, str):
                if not any(s in valor_sabor.lower() for s in sabores_lista):
                    return False
            else:
                return False

        # ¿Cumple el objetivo?
        if objetivos_lista:
            valor_obj = fila.objetivo
            if isinstance(valor_obj, list):
                if not any(str(item).lower() in objetivos_lista for item in valor_obj):
                    return False
            elif isinstance(valor_obj, str):
                if not any(o in valor_obj.lower() for o in objetivos_lista):
                    return False
            else:
                return False

        return True

    if sabores_lista or objetivos_lista:
        datos_filtrados = [d for d in datos_raw if cumple_filtros_arrays(d)]
    else:
        datos_filtrados = datos_raw

    # 9. Paginación y Carga Real de los Productos Finales
    total_resultados = len(datos_filtrados)
    offset_real = skip if skip > 0 else (page - 1) * limit
    
    # Extraemos SOLO los IDs que pertenecen a la página actual (ej. 36 IDs)
    ids_pagina = [d.id for d in datos_filtrados[offset_real: offset_real + limit]]
    
    productos = []
    if ids_pagina:
        # Hacemos una única query final para traer SOLO los 36 objetos completos
        productos_bd = (
            db.query(models.Producto)
            .options(
                selectinload(models.Producto.ofertas)
                .selectinload(models.Oferta.historial_precios)
            )
            .filter(models.Producto.id.in_(ids_pagina))
            .all()
        )
        
        # Volvemos a ordenarlos según el orden exacto que determinó la query principal (ids_pagina)
        productos_dict = {p.id: p for p in productos_bd}
        productos = [productos_dict[id_] for id_ in ids_pagina if id_ in productos_dict]

    return {"total_resultados": total_resultados, "productos": productos}
