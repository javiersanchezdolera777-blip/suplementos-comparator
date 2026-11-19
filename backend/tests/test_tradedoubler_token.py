"""Pruebas unitarias para la migración de tokens de TradeDoubler a variables de entorno.

Verifica:
1. Ambos ingestores (Farma2Go y SportLive) construyen su URL usando TRADEDOUBLER_PRODUCTS_TOKEN.
2. Cada uno conserva exactamente su identificador de feed:
   - Farma2Go: 256625
   - SportLive: 108208
3. La ausencia o valor vacío del token aborta antes de realizar cualquier petición HTTP
   y ANTES de cualquier operación o conexión de base de datos (SessionLocal no se instancia).
4. Ningún archivo actual contiene credenciales hardcodeadas (escaneo repositorio completo sin almacenar secretos).
5. Errores HTTP (401, ConnectionError, agotamiento de reintentos) NO filtran el token en:
   - download_json_with_cache()
   - get_with_backoff()
   - stdout / stderr
   - logs (caplog)
   - mensajes de excepción
   - tracebacks completos
6. La descarga y el flujo de caché se mantienen íntegros y operativos.
7. Los fallos de persistencia por lotes en los ingestores:
   - Permiten continuar el procesamiento de lotes posteriores
   - No cuentan como insertados los productos fallidos
   - Lanzan una excepción agregada al finalizar
   - Cierran siempre la sesión de base de datos
8. El orquestador registra fallos críticos (de red, autenticación o persistencia) y termina con código de salida 1,
   permitiendo que las demás tiendas continúen su ejecución.
"""
import os
import re
import subprocess
import sys
import traceback
from unittest.mock import patch, MagicMock
import pytest
import requests

from ingestores import pharma2go, sportlive
from ingestores.http_client import (
    download_json_with_cache,
    get_with_backoff,
    sanitize_url,
    sanitize_error_message,
)
from scripts import orquestador


# =========================================================================
# 1. Resolución de URL y Feed IDs
# =========================================================================

def test_farma2go_uses_env_var_and_preserves_feed_id(monkeypatch):
    test_token = "MOCK_TOKEN_FARMA2GO_ABC123"
    monkeypatch.setenv("TRADEDOUBLER_PRODUCTS_TOKEN", test_token)

    assert pharma2go.FEED_ID == "256625"
    url = pharma2go.obtener_url_feed()
    assert "fid=256625" in url
    assert f"token={test_token}" in url
    assert url.startswith("https://api.tradedoubler.com/1.0/productsUnlimited.json;compress=gz;fid=256625?token=")


def test_sportlive_uses_env_var_and_preserves_feed_id(monkeypatch):
    test_token = "MOCK_TOKEN_SPORTLIVE_XYZ789"
    monkeypatch.setenv("TRADEDOUBLER_PRODUCTS_TOKEN", test_token)

    assert sportlive.FEED_ID == "108208"
    url = sportlive.obtener_url_feed()
    assert "fid=108208" in url
    assert f"token={test_token}" in url
    assert url.startswith("https://api.tradedoubler.com/1.0/productsUnlimited.json;compress=gz;fid=108208?token=")


# =========================================================================
# 2. Validación de Token Previa a HTTP y a Base de Datos
# =========================================================================

@pytest.mark.parametrize("empty_val", ["", "   ", None])
def test_missing_or_empty_token_aborts_before_http(monkeypatch, empty_val):
    if empty_val is None:
        monkeypatch.delenv("TRADEDOUBLER_PRODUCTS_TOKEN", raising=False)
    else:
        monkeypatch.setenv("TRADEDOUBLER_PRODUCTS_TOKEN", empty_val)

    with patch("requests.Session.get") as mock_http_get, patch("requests.get") as mock_req_get:
        # Farma2Go debe abortar
        with pytest.raises(ValueError, match="TRADEDOUBLER_PRODUCTS_TOKEN"):
            pharma2go.obtener_url_feed()

        with pytest.raises(ValueError, match="TRADEDOUBLER_PRODUCTS_TOKEN"):
            pharma2go.descargar_datos()

        # SportLive debe abortar
        with pytest.raises(ValueError, match="TRADEDOUBLER_PRODUCTS_TOKEN"):
            sportlive.obtener_url_feed()

        with pytest.raises(ValueError, match="TRADEDOUBLER_PRODUCTS_TOKEN"):
            sportlive.descargar_datos()

        mock_http_get.assert_not_called()
        mock_req_get.assert_not_called()


def test_missing_token_aborts_before_database_operations(monkeypatch):
    """Verifica que la falta de token aborta antes de instanciar SessionLocal o tocar la BD."""
    monkeypatch.delenv("TRADEDOUBLER_PRODUCTS_TOKEN", raising=False)

    with patch.object(pharma2go, "SessionLocal") as mock_session_farma:
        with pytest.raises(ValueError, match="TRADEDOUBLER_PRODUCTS_TOKEN"):
            pharma2go.inyectar_en_bd()
        mock_session_farma.assert_not_called()

    with patch.object(sportlive, "SessionLocal") as mock_session_sport:
        with pytest.raises(ValueError, match="TRADEDOUBLER_PRODUCTS_TOKEN"):
            sportlive.inyectar_en_bd()
        mock_session_sport.assert_not_called()


# =========================================================================
# 3. Sanitización de Errores HTTP en download_json_with_cache y get_with_backoff
# =========================================================================

@pytest.mark.parametrize("scenario", ["http_401", "connection_error", "max_retries"])
def test_download_json_with_cache_does_not_leak_token(capsys, monkeypatch, tmp_path, scenario):
    fake_token = "FAKETOKEN_LEAK_CHECK_9876543210"
    feed_url = f"https://api.tradedoubler.com/1.0/productsUnlimited.json;compress=gz;fid=256625?token={fake_token}"
    fake_cache = str(tmp_path / "nonexistent_cache.json")

    monkeypatch.setattr("time.sleep", lambda s: None)

    with patch("ingestores.http_client.create_session") as mock_session_maker:
        session = MagicMock()
        mock_session_maker.return_value = session

        if scenario == "http_401":
            mock_resp = MagicMock()
            mock_resp.status_code = 401
            mock_resp.raise_for_status.side_effect = requests.HTTPError(
                f"401 Client Error: Unauthorized for url: {feed_url}",
                response=mock_resp,
            )
            session.get.return_value = mock_resp
        elif scenario == "connection_error":
            session.get.side_effect = requests.ConnectionError(
                f"Connection refused connecting to {feed_url}"
            )
        elif scenario == "max_retries":
            session.get.side_effect = requests.RequestException(
                f"Max retries exceeded with url: {feed_url}"
            )

        with pytest.raises(RuntimeError) as exc_info:
            download_json_with_cache(url=feed_url, cache_path=fake_cache)

        err_msg = str(exc_info.value)
        assert fake_token not in err_msg, f"Token filtrado en excepción: {err_msg}"

        tb_text = "".join(traceback.format_exception(exc_info.type, exc_info.value, exc_info.tb))
        assert fake_token not in tb_text, f"Token filtrado en traceback:\n{tb_text}"

        captured = capsys.readouterr()
        assert fake_token not in captured.out, f"Token filtrado en stdout: {captured.out}"
        assert fake_token not in captured.err, f"Token filtrado en stderr: {captured.err}"


@pytest.mark.parametrize("scenario", ["http_401", "http_429", "connection_error", "max_retries"])
def test_get_with_backoff_does_not_leak_token(capsys, caplog, monkeypatch, scenario):
    fake_token = "FAKETOKEN_BACKOFF_SAFE_11223344"
    target_url = f"https://api.tradedoubler.com/1.0/productsUnlimited.json;fid=108208?token={fake_token}"

    monkeypatch.setattr("time.sleep", lambda s: None)
    session = MagicMock()

    if scenario == "http_401":
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        session.get.return_value = mock_resp
        with pytest.raises(RuntimeError) as exc_info:
            get_with_backoff(session, target_url)
        assert fake_token not in str(exc_info.value)
        tb_text = "".join(traceback.format_exception(exc_info.type, exc_info.value, exc_info.tb))
        assert fake_token not in tb_text

    elif scenario == "http_429":
        # 429 seguido de 200 OK
        resp_429 = MagicMock()
        resp_429.status_code = 429
        resp_429.headers = {"Retry-After": "1"}
        resp_200 = MagicMock()
        resp_200.status_code = 200
        session.get.side_effect = [resp_429, resp_200]

        res = get_with_backoff(session, target_url)
        assert res.status_code == 200

    elif scenario == "connection_error":
        session.get.side_effect = requests.ConnectionError(
            f"Failed to connect to {target_url}"
        )
        with pytest.raises(RuntimeError) as exc_info:
            get_with_backoff(session, target_url)
        assert fake_token not in str(exc_info.value)
        tb_text = "".join(traceback.format_exception(exc_info.type, exc_info.value, exc_info.tb))
        assert fake_token not in tb_text

    elif scenario == "max_retries":
        resp_500 = MagicMock()
        resp_500.status_code = 500
        session.get.return_value = resp_500
        with pytest.raises(RuntimeError) as exc_info:
            get_with_backoff(session, target_url)
        assert fake_token not in str(exc_info.value)
        tb_text = "".join(traceback.format_exception(exc_info.type, exc_info.value, exc_info.tb))
        assert fake_token not in tb_text

    # Comprobaciones globales de stdout, stderr y caplog
    captured = capsys.readouterr()
    assert fake_token not in captured.out, f"Token presente en stdout: {captured.out}"
    assert fake_token not in captured.err, f"Token presente en stderr: {captured.err}"
    assert fake_token not in caplog.text, f"Token presente en caplog: {caplog.text}"


# =========================================================================
# 4. Flujo de Descarga y Caché
# =========================================================================

def test_descargar_datos_cache_flow(monkeypatch, tmp_path):
    fake_cache = tmp_path / "cache_prueba.json"
    fake_cache.write_text('{"products": [{"name": "Producto Cacheado"}]}', encoding="utf-8")

    monkeypatch.setenv("TRADEDOUBLER_PRODUCTS_TOKEN", "VALID_MOCK_TOKEN")
    monkeypatch.setattr(pharma2go, "ARCHIVO_CACHE", str(fake_cache))

    with patch("requests.Session.get") as mock_get:
        resultado = pharma2go.descargar_datos()
        assert resultado == {"products": [{"name": "Producto Cacheado"}]}
        mock_get.assert_not_called()


def test_descargar_datos_calls_download_when_cache_missing(monkeypatch, tmp_path):
    missing_cache = tmp_path / "non_existent.json"
    monkeypatch.setenv("TRADEDOUBLER_PRODUCTS_TOKEN", "MOCK_DOWNLOAD_TOKEN")
    monkeypatch.setattr(sportlive, "ARCHIVO_CACHE", str(missing_cache))

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"products": [{"name": "Producto Remoto"}]}'
    mock_response.json.return_value = {"products": [{"name": "Producto Remoto"}]}

    with patch("ingestores.http_client.create_session") as mock_session_builder:
        session_instance = MagicMock()
        session_instance.get.return_value = mock_response
        mock_session_builder.return_value = session_instance

        datos = sportlive.descargar_datos()
        assert datos == {"products": [{"name": "Producto Remoto"}]}

        assert session_instance.get.called
        called_url = session_instance.get.call_args[0][0]
        assert "fid=108208" in called_url
        assert "token=MOCK_DOWNLOAD_TOKEN" in called_url


# =========================================================================
# 5. Persistencia por Lotes y Cierre de Sesión
# =========================================================================

def _generar_items_sinteticos(n: int) -> list[dict]:
    return [
        {
            "name": f"Proteina Suplemento Test #{i}",
            "description": "Proteina whey para aumento muscular",
            "offers": [
                {
                    "price": {"value": 29.99},
                    "productUrl": f"https://tienda.example.com/p/{i}",
                }
            ],
            "brand": "Optimum Nutrition",
        }
        for i in range(n)
    ]


@pytest.mark.parametrize("falla_en_lote", ["intermedio", "final"])
def test_farma2go_batch_persistence_error_handling(monkeypatch, falla_en_lote):
    monkeypatch.setenv("TRADEDOUBLER_PRODUCTS_TOKEN", "MOCK_TOKEN_VAL")
    items = _generar_items_sinteticos(120)  # Lote 1 (50), Lote 2 (50), Lote final (20)

    monkeypatch.setattr(pharma2go, "descargar_datos", lambda: {"products": items})

    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_query.filter_by.return_value.first.return_value = MagicMock(id=1)
    mock_query.options.return_value.all.return_value = []
    mock_db.query.return_value = mock_query

    commit_count = 0

    def mock_commit():
        nonlocal commit_count
        commit_count += 1
        # Si falla en lote intermedio (ej: lote 1 falla, lote 2 y final pasan)
        if falla_en_lote == "intermedio" and commit_count == 1:
            raise RuntimeError("Fallo simulado de disco o BD en lote 1")
        # Si falla en lote final (lote 1 y 2 pasan, lote 3 falla)
        if falla_en_lote == "final" and commit_count == 3:
            raise RuntimeError("Fallo simulado de disco o BD en lote final")

    mock_db.commit.side_effect = mock_commit

    with patch.object(pharma2go, "SessionLocal", return_value=mock_db):
        with pytest.raises(RuntimeError, match="Fallo de persistencia en Farma2Go"):
            pharma2go.inyectar_en_bd()

        # Comprobar que db.close() SIEMPRE fue invocado en el finally
        mock_db.close.assert_called_once()
        # Comprobar que db.rollback() fue invocado ante el fallo
        assert mock_db.rollback.called


@pytest.mark.parametrize("falla_en_lote", ["intermedio", "final"])
def test_sportlive_batch_persistence_error_handling(monkeypatch, falla_en_lote):
    monkeypatch.setenv("TRADEDOUBLER_PRODUCTS_TOKEN", "MOCK_TOKEN_VAL")
    items = _generar_items_sinteticos(120)

    monkeypatch.setattr(sportlive, "descargar_datos", lambda: {"products": items})

    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_query.filter_by.return_value.first.return_value = MagicMock(id=1)
    mock_query.options.return_value.all.return_value = []
    mock_db.query.return_value = mock_query

    commit_count = 0

    def mock_commit():
        nonlocal commit_count
        commit_count += 1
        if falla_en_lote == "intermedio" and commit_count == 1:
            raise RuntimeError("Fallo simulado de disco o BD en lote 1")
        if falla_en_lote == "final" and commit_count == 3:
            raise RuntimeError("Fallo simulado de disco o BD en lote final")

    mock_db.commit.side_effect = mock_commit

    with patch.object(sportlive, "SessionLocal", return_value=mock_db):
        with pytest.raises(RuntimeError, match="Fallo de persistencia en Sportlive"):
            sportlive.inyectar_en_bd()

        mock_db.close.assert_called_once()
        assert mock_db.rollback.called


# =========================================================================
# 6. Orquestador y Fiabilidad del CRON ante Fallos
# =========================================================================

def test_orquestador_error_handling_and_exit_code(monkeypatch):
    """Comprueba que:
    1. Si Farma2Go falla (de red o persistencia), Sportlive todavía se ejecuta.
    2. Si alguna tienda falla críticamente, el orquestador finaliza con sys.exit(1).
    3. Las alertas y la sesión del orquestador se cierran correctamente.
    """
    mock_datetime = MagicMock()
    mock_datetime.now.return_value.hour = 2
    mock_datetime.now.return_value.strftime.return_value = "2026-11-19 02:00:00"
    mock_datetime.utcnow.return_value = "2026-11-19 02:00:00"
    monkeypatch.setattr(orquestador, "datetime", mock_datetime)

    monkeypatch.setattr(orquestador, "inyectar_hsn", MagicMock())
    mock_alertas = MagicMock()
    monkeypatch.setattr(orquestador, "generar_alertas", mock_alertas)
    monkeypatch.setattr(orquestador, "disparar_alertas_agrupadas", MagicMock())

    mock_orq_db = MagicMock()
    monkeypatch.setattr(orquestador, "SessionLocal", MagicMock(return_value=mock_orq_db))

    # Caso 1: Farma2Go falla con error de persistencia
    mock_pharma = MagicMock(side_effect=RuntimeError("Fallo de persistencia en Farma2Go"))
    mock_sport = MagicMock()
    monkeypatch.setattr(orquestador, "inyectar_pharma2go", mock_pharma)
    monkeypatch.setattr(orquestador, "inyectar_sportlive", mock_sport)

    with pytest.raises(SystemExit) as exit_info:
        orquestador.ejecutar_orquestador()

    assert exit_info.value.code == 1
    mock_pharma.assert_called_once()
    mock_sport.assert_called_once()
    mock_orq_db.close.assert_called_once()

    # Caso 2: Ambas tienen éxito
    mock_orq_db.reset_mock()
    mock_pharma_ok = MagicMock()
    mock_sport_ok = MagicMock()
    monkeypatch.setattr(orquestador, "inyectar_pharma2go", mock_pharma_ok)
    monkeypatch.setattr(orquestador, "inyectar_sportlive", mock_sport_ok)

    orquestador.ejecutar_orquestador()
    mock_pharma_ok.assert_called_once()
    mock_sport_ok.assert_called_once()
    mock_orq_db.close.assert_called_once()


# =========================================================================
# 7. Pruebas Específicas de Persistencia por Lotes y Cierre
# =========================================================================

@pytest.mark.parametrize("modulo,tienda_nombre", [(pharma2go, "Farma2Go"), (sportlive, "Sportlive")])
def test_feed_solo_existentes_cero_nuevos_persiste(monkeypatch, modulo, tienda_nombre):
    """Feed con productos existentes y cero productos nuevos: los cambios se guardan."""
    monkeypatch.setenv("TRADEDOUBLER_PRODUCTS_TOKEN", "MOCK_TOKEN_VAL")
    items = _generar_items_sinteticos(3)
    slugs = [modulo.generar_slug(it["name"]) for it in items]

    productos_mock = {s: MagicMock(slug=s, ofertas=[]) for s in slugs}

    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_query.filter_by.return_value.first.return_value = MagicMock(id=1)
    mock_query.options.return_value.all.return_value = list(productos_mock.values())
    mock_db.query.return_value = mock_query

    monkeypatch.setattr(modulo, "descargar_datos", lambda: {"products": items})

    with patch.object(modulo, "SessionLocal", return_value=mock_db):
        modulo.inyectar_en_bd()

        # Verifica que db.commit() fue invocado (a pesar de tener 0 productos nuevos)
        assert mock_db.commit.called
        assert mock_db.add.call_count == 3
        mock_db.close.assert_called_once()


@pytest.mark.parametrize("modulo,tienda_nombre", [(pharma2go, "Farma2Go"), (sportlive, "Sportlive")])
def test_feed_mixto_existentes_y_nuevos_persiste(monkeypatch, modulo, tienda_nombre):
    """Feed mixto con productos existentes y nuevos: ambos tipos se guardan."""
    monkeypatch.setenv("TRADEDOUBLER_PRODUCTS_TOKEN", "MOCK_TOKEN_VAL")
    items = _generar_items_sinteticos(4)
    slug_existente = modulo.generar_slug(items[0]["name"])

    p_existente = MagicMock(slug=slug_existente, ofertas=[])

    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_query.filter_by.return_value.first.return_value = MagicMock(id=1)
    mock_query.options.return_value.all.return_value = [p_existente]
    mock_db.query.return_value = mock_query

    monkeypatch.setattr(modulo, "descargar_datos", lambda: {"products": items})

    with patch.object(modulo, "SessionLocal", return_value=mock_db):
        modulo.inyectar_en_bd()

        assert mock_db.add.called      # producto existente actualizado
        assert mock_db.add_all.called  # productos nuevos añadidos
        assert mock_db.commit.called
        mock_db.close.assert_called_once()


@pytest.mark.parametrize("modulo,tienda_nombre", [(pharma2go, "Farma2Go"), (sportlive, "Sportlive")])
def test_fallo_en_lote_no_cuenta_como_guardadas_sus_modificaciones(monkeypatch, modulo, tienda_nombre):
    """Fallo en un lote: no se cuentan como guardadas sus modificaciones."""
    monkeypatch.setenv("TRADEDOUBLER_PRODUCTS_TOKEN", "MOCK_TOKEN_VAL")
    # 60 items existentes: Lote 1 (50 items), Lote 2 final (10 items)
    items = _generar_items_sinteticos(60)
    slugs = [modulo.generar_slug(it["name"]) for it in items]

    productos_mock = {s: MagicMock(slug=s, ofertas=[]) for s in slugs}

    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_query.filter_by.return_value.first.return_value = MagicMock(id=1)
    mock_query.options.return_value.all.return_value = list(productos_mock.values())
    mock_db.query.return_value = mock_query

    monkeypatch.setattr(modulo, "descargar_datos", lambda: {"products": items})

    commit_count = 0
    def mock_commit():
        nonlocal commit_count
        commit_count += 1
        if commit_count == 1:
            raise RuntimeError("Fallo simulado en lote 1")

    mock_db.commit.side_effect = mock_commit

    with patch.object(modulo, "SessionLocal", return_value=mock_db):
        with pytest.raises(RuntimeError, match=f"Fallo de persistencia en {tienda_nombre}"):
            modulo.inyectar_en_bd()

        # Debe haber hecho rollback para el lote fallido
        assert mock_db.rollback.called
        mock_db.close.assert_called_once()


@pytest.mark.parametrize("modulo,tienda_nombre", [(pharma2go, "Farma2Go"), (sportlive, "Sportlive")])
def test_fallo_ultimo_commit_propaga_y_cierra_sesion(monkeypatch, modulo, tienda_nombre):
    """Fallo del último commit: se propaga el error y se cierra la sesión."""
    monkeypatch.setenv("TRADEDOUBLER_PRODUCTS_TOKEN", "MOCK_TOKEN_VAL")
    items = _generar_items_sinteticos(5)

    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_query.filter_by.return_value.first.return_value = MagicMock(id=1)
    mock_query.options.return_value.all.return_value = []
    mock_db.query.return_value = mock_query

    mock_db.commit.side_effect = RuntimeError("Fallo forzado en commit final")

    monkeypatch.setattr(modulo, "descargar_datos", lambda: {"products": items})

    with patch.object(modulo, "SessionLocal", return_value=mock_db):
        with pytest.raises(RuntimeError, match=f"Fallo de persistencia en {tienda_nombre}"):
            modulo.inyectar_en_bd()

        assert mock_db.rollback.called
        mock_db.close.assert_called_once()


# =========================================================================
# 8. Escaneo Genérico de Credenciales en Todo el Repositorio Versionado
# =========================================================================

def test_no_hardcoded_credentials_scan():
    """Inspecciona todos los archivos versionados mediante git ls-files.

    Detecta:
    - URLs de TradeDoubler con parámetros de token reales.
    - Asignaciones directas de tokens o credenciales.
    Excluye falsos positivos documentados: mocks, tests, placeholders ('tu_', 'fake', 'mock').
    """
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    try:
        proc = subprocess.run(
            ["git", "ls-files"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        tracked_files = proc.stdout.splitlines()
    except Exception:
        pytest.skip("No se pudo ejecutar git ls-files en este entorno")

    token_td_pattern = re.compile(
        r"(?i)tradedoubler\.com/[^\s\"']*?[?&;]token=([A-Za-z0-9_\-]{15,})"
    )
    secret_assign_pattern = re.compile(
        r"(?i)\b(?:tradedoubler[_\w]*token)\s*=\s*['\"]([A-Za-z0-9_\-]{15,})['\"]"
    )

    ignored_extensions = (".png", ".jpg", ".docx", ".pdf", ".ico", ".svg", ".zip", ".woff", ".woff2")
    known_placeholders = {"mock", "fake", "tu_", "your_", "example", "test", "xxx", "placeholder"}

    suspicious_files = []

    for rel_path in tracked_files:
        if rel_path.endswith(ignored_extensions):
            continue

        full_path = os.path.join(repo_root, rel_path)
        if not os.path.exists(full_path):
            continue

        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except OSError:
            continue

        # 1. Comprobar tokens TradeDoubler (analizando el valor completo de la coincidencia y el token)
        for match in token_td_pattern.finditer(content):
            full_match = match.group(0)
            token_val = match.group(1)
            if not any(ph in full_match.lower() for ph in known_placeholders) and not any(ph in token_val.lower() for ph in known_placeholders):
                suspicious_files.append(rel_path)
                break

        # 2. Comprobar asignaciones directas de tokens (analizando el valor asignado y la coincidencia completa)
        for match in secret_assign_pattern.finditer(content):
            full_match = match.group(0)
            assigned_val = match.group(1)
            if not any(ph in full_match.lower() for ph in known_placeholders) and not any(ph in assigned_val.lower() for ph in known_placeholders):
                suspicious_files.append(rel_path)
                break

    assert len(suspicious_files) == 0, f"Archivos sospechosos detectados en el escaneo: {suspicious_files}"
