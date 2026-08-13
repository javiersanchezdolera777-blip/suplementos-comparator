import csv
import io
import json
import re
from typing import Any, Dict, List, Optional

from ingestores.http_client import create_session, download_json_with_cache


def sanitizar_precio(valor_crudo: Any) -> Optional[float]:
    """
    Limpia y sanitiza cadenas o números de precio ("29,99 €", "1.250,00", "15.5 EUR")
    convirtiéndolos a un flotante válido. Retorna None si no se puede interpretar.
    """
    if valor_crudo is None:
        return None

    if isinstance(valor_crudo, (int, float)):
        return float(valor_crudo)

    texto = str(valor_crudo).strip()
    if not texto:
        return None

    # Quitar símbolos de moneda y texto no numérico excepto puntos, comas y guiones
    texto_limpio = re.sub(r'[^\d.,\-]', '', texto).strip()

    if not texto_limpio:
        return None

    # Caso: Tanto punto como coma presentes (ej: "1.250,99" o "1,250.99")
    if '.' in texto_limpio and ',' in texto_limpio:
        pos_punto = texto_limpio.rfind('.')
        pos_coma = texto_limpio.rfind(',')
        if pos_coma > pos_punto:
            # Formato europeo: 1.250,99 -> 1250.99
            texto_limpio = texto_limpio.replace('.', '').replace(',', '.')
        else:
            # Formato anglosajón: 1,250.99 -> 1250.99
            texto_limpio = texto_limpio.replace(',', '')
    elif ',' in texto_limpio:
        # Formato solo coma: "29,99" -> "29.99"
        texto_limpio = texto_limpio.replace(',', '.')

    try:
        val = float(texto_limpio)
        return val if val >= 0 else None
    except ValueError:
        return None


def descargar_y_parsear_feed(
    url: str,
    formato: str = "json",
    delimitador: str = ",",
    encoding: str = "utf-8",
    cache_path: Optional[str] = None,
    ttl_hours: int = 12
) -> List[Dict[str, Any]]:
    """
    Descarga y parsea un feed de afiliados en formato JSON, CSV o TSV.
    Maneja decodificación con fallback a latin-1/utf-8-sig.
    """
    fmt = formato.lower().strip()

    if fmt == "json":
        datos = download_json_with_cache(
            url=url,
            cache_path=cache_path,
            ttl_hours=ttl_hours,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SuplementosComparatorBot/1.0",
                "Accept": "application/json, application/gzip",
            }
        )
        if isinstance(datos, list):
            return datos
        if isinstance(datos, dict):
            return datos.get("products") or datos.get("productos") or datos.get("data") or [datos]
        return []

    # Para CSV / TSV / Archivos de texto
    session = create_session()
    response = session.get(url, timeout=45)
    response.raise_for_status()
    contenido_bytes = response.content

    # Estrategia de decodificación con fallback
    texto = ""
    for enc in [encoding, "utf-8-sig", "utf-8", "latin-1", "cp1252"]:
        try:
            texto = contenido_bytes.decode(enc)
            break
        except (UnicodeDecodeError, TypeError):
            continue

    if not texto:
        texto = contenido_bytes.decode("utf-8", errors="ignore")

    if fmt == "tsv":
        delimitador = "\t"

    f = io.StringIO(texto)
    reader = csv.DictReader(f, delimiter=delimitador)
    items = []
    for row in reader:
        items.append(dict(row))

    return items
