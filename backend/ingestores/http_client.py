import gzip
import io
import json
import os
import random
import re
import time
import zipfile
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SuplementosComparatorBot/1.0",
    "Accept": "application/json, application/gzip, text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
    "Connection": "keep-alive",
}

SENSITIVE_PARAMS = {"token", "access_token", "api_key", "key", "secret", "password"}


def sanitize_url(url: str) -> str:
    """Sanitiza una URL enmascarando cualquier parámetro sensible (token, key, secret, etc.)."""
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        if parsed.query:
            query_pairs = parse_qsl(parsed.query, keep_blank_values=True)
            sanitized_pairs = []
            for k, v in query_pairs:
                if k.lower() in SENSITIVE_PARAMS:
                    sanitized_pairs.append((k, "***"))
                else:
                    sanitized_pairs.append((k, v))
            sanitized_query = urlencode(sanitized_pairs)
            url = urlunparse(parsed._replace(query=sanitized_query))
    except Exception:
        pass

    # Regex secundaria para capturar parámetros en query o matriz (ej: ?token=... o ;token=...)
    return re.sub(
        r"(?i)(token|access_token|api_key|key|secret|password)=([^&;\s'\"]+)",
        r"\1=***",
        url,
    )


def sanitize_error_message(msg: str) -> str:
    """Elimina o enmascara parámetros sensibles que aparezcan en mensajes de error o URLs."""
    if not msg:
        return ""
    return re.sub(
        r"(?i)(token|access_token|api_key|key|secret|password)=([^&;\s'\"]+)",
        r"\1=***",
        str(msg),
    )


def create_session(headers: Optional[Dict[str, str]] = None) -> requests.Session:
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    if headers:
        session.headers.update(headers)

    retry_strategy = Retry(
        total=4,
        connect=2,
        read=2,
        status=4,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        backoff_factor=1.5,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def _read_cache(cache_path: str, ttl_hours: int, allow_stale: bool = False) -> Optional[Any]:
    candidate_paths = [cache_path]
    if cache_path.startswith(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))):
        legacy_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "cache_ingestores",
            os.path.basename(cache_path),
        )
        if legacy_path not in candidate_paths:
            candidate_paths.append(legacy_path)

    for candidate in candidate_paths:
        if not os.path.exists(candidate):
            continue

        try:
            modified_at = datetime.fromtimestamp(os.path.getmtime(candidate))
        except OSError:
            continue

        age_hours = (datetime.now() - modified_at).total_seconds() / 3600
        if age_hours < ttl_hours:
            try:
                with open(candidate, "r", encoding="utf-8") as fh:
                    if candidate != cache_path:
                        print(f"✅ Usando caché antigua desde {candidate}")
                    return json.load(fh)
            except (json.JSONDecodeError, OSError):
                print("⚠️ La caché estaba corrupta. Se volverá a descargar.")
                try:
                    os.remove(candidate)
                except OSError:
                    pass
        elif allow_stale:
            try:
                with open(candidate, "r", encoding="utf-8") as fh:
                    print(f"⚠️ Usando caché antigua ({age_hours:.1f}h) desde {candidate} porque la descarga falló.")
                    return json.load(fh)
            except (json.JSONDecodeError, OSError):
                continue

    return None


def _write_cache(cache_path: str, payload: Any) -> None:
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=4)


def download_json_with_cache(
    url: str,
    cache_path: str,
    ttl_hours: int = 12,
    timeout: int = 45,
    headers: Optional[Dict[str, str]] = None,
) -> Any:
    cached = _read_cache(cache_path, ttl_hours, allow_stale=True)
    if cached is not None:
        print(f"✅ Usando caché válida o antigua en {cache_path}")
        return cached

    session = create_session(headers)
    last_error_desc: Optional[str] = None
    sanitized_url = sanitize_url(url)

    for attempt in range(1, 5):
        if attempt > 1:
            delay = min(60, 2 ** (attempt - 1)) + round(random.uniform(0, 1.5), 2)
            print(f"⏳ Reintento {attempt}/4 en {delay:.1f}s...")
            time.sleep(delay)

        try:
            response = session.get(url, timeout=timeout)
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                wait_seconds = (
                    int(retry_after)
                    if retry_after and retry_after.isdigit()
                    else min(60, 2 ** attempt)
                )
                print(f"⚠️ 429 recibido en {sanitized_url}. Esperando {wait_seconds}s antes de reintentar...")
                time.sleep(wait_seconds)
                continue

            if response.status_code != 200:
                raise RuntimeError(
                    f"Error HTTP {response.status_code} al descargar el feed desde {sanitized_url}"
                )

            try:
                content = gzip.decompress(response.content)
                payload = json.loads(content.decode("utf-8"))
            except OSError:
                try:
                    payload = response.json()
                except ValueError:
                    print("⚠️ La respuesta no era un JSON válido. Se intentará como ZIP...")
                    try:
                        with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                            payload = json.load(zf.open(zf.namelist()[0]))
                    except Exception as exc:
                        raise RuntimeError(f"No se pudo interpretar la respuesta del feed: {exc}") from None

            _write_cache(cache_path, payload)
            return payload

        except requests.RequestException as exc:
            sanitized_err = sanitize_error_message(str(exc))
            err_type = type(exc).__name__
            status_code = getattr(getattr(exc, "response", None), "status_code", None)
            status_str = f" (Status {status_code})" if status_code else ""
            last_error_desc = f"{err_type}{status_str}: {sanitized_err}"

            if attempt == 4:
                raise RuntimeError(
                    f"No se pudo descargar el feed tras 4 intentos [{last_error_desc}] desde {sanitized_url}"
                ) from None
        except RuntimeError as exc:
            sanitized_msg = sanitize_error_message(str(exc))
            raise RuntimeError(sanitized_msg) from None

    if last_error_desc is not None:
        raise RuntimeError(
            f"No se pudo completar la descarga del feed tras reintentos [{last_error_desc}] desde {sanitized_url}"
        ) from None

    raise RuntimeError(f"No se pudo completar la descarga del feed desde {sanitized_url}")


def get_with_backoff(session: requests.Session, url: str, timeout: int = 30) -> requests.Response:
    sanitized_url = sanitize_url(url)
    for attempt in range(1, 5):
        if attempt > 1:
            delay = min(60, 2 ** (attempt - 1)) + round(random.uniform(0, 1.5), 2)
            time.sleep(delay)

        try:
            response = session.get(url, timeout=timeout)
        except requests.RequestException as exc:
            sanitized_err = sanitize_error_message(str(exc))
            if attempt == 4:
                raise RuntimeError(
                    f"Error de red tras 4 intentos [{type(exc).__name__}: {sanitized_err}] en {sanitized_url}"
                ) from None
            continue

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            wait_seconds = (
                int(retry_after)
                if retry_after and retry_after.isdigit()
                else min(60, 2 ** attempt)
            )
            print(f"⚠️ 429 recibido al acceder a {sanitized_url}. Esperando {wait_seconds}s...")
            time.sleep(wait_seconds)
            continue

        if response.status_code in {500, 502, 503, 504}:
            if attempt == 4:
                raise RuntimeError(
                    f"Error del servidor HTTP {response.status_code} tras 4 intentos en {sanitized_url}"
                )
            continue

        if response.status_code != 200:
            raise RuntimeError(
                f"Error HTTP {response.status_code} al consultar {sanitized_url}"
            )

        return response

    raise RuntimeError(f"No se pudo completar la petición tras 4 intentos en {sanitized_url}")
