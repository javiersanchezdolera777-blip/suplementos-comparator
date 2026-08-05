import gzip
import io
import json
import os
import random
import time
import zipfile
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SuplementosComparatorBot/1.0",
    "Accept": "application/json, application/gzip, text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
    "Connection": "keep-alive",
}


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
        legacy_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache_ingestores", os.path.basename(cache_path))
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

    try:
        modified_at = datetime.fromtimestamp(os.path.getmtime(cache_path))
    except OSError:
        return None

    age_hours = (datetime.now() - modified_at).total_seconds() / 3600
    if age_hours < ttl_hours:
        try:
            with open(cache_path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            print("⚠️ La caché estaba corrupta. Se volverá a descargar.")
            try:
                os.remove(cache_path)
            except OSError:
                pass
    elif allow_stale:
        try:
            with open(cache_path, "r", encoding="utf-8") as fh:
                print(f"⚠️ Usando caché antigua ({age_hours:.1f}h) porque la descarga falló.")
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            return None
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
    last_error: Optional[Exception] = None

    for attempt in range(1, 5):
        if attempt > 1:
            delay = min(60, 2 ** (attempt - 1)) + round(random.uniform(0, 1.5), 2)
            print(f"⏳ Reintento {attempt}/4 en {delay:.1f}s...")
            time.sleep(delay)

        try:
            response = session.get(url, timeout=timeout)
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                wait_seconds = int(retry_after) if retry_after and retry_after.isdigit() else min(60, 2 ** attempt)
                print(f"⚠️ 429 recibido. Esperando {wait_seconds}s antes de reintentar...")
                time.sleep(wait_seconds)
                continue

            response.raise_for_status()

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
                        raise RuntimeError(f"No se pudo interpretar la respuesta del feed: {exc}") from exc

            _write_cache(cache_path, payload)
            return payload
        except requests.RequestException as exc:
            last_error = exc
            if attempt == 4:
                raise RuntimeError(f"No se pudo descargar el feed tras 4 intentos: {exc}") from exc

    if last_error is not None:
        raise RuntimeError(f"No se pudo completar la descarga del feed: {last_error}") from last_error

    raise RuntimeError("No se pudo completar la descarga del feed")


def get_with_backoff(session: requests.Session, url: str, timeout: int = 30) -> requests.Response:
    for attempt in range(1, 5):
        if attempt > 1:
            delay = min(60, 2 ** (attempt - 1)) + round(random.uniform(0, 1.5), 2)
            time.sleep(delay)

        response = session.get(url, timeout=timeout)
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            wait_seconds = int(retry_after) if retry_after and retry_after.isdigit() else min(60, 2 ** attempt)
            print(f"⚠️ 429 recibido al acceder a {url}. Esperando {wait_seconds}s...")
            time.sleep(wait_seconds)
            continue

        if response.status_code in {500, 502, 503, 504}:
            if attempt == 4:
                response.raise_for_status()
            continue

        response.raise_for_status()
        return response

    raise RuntimeError(f"No se pudo completar la petición tras 4 intentos: {url}")
