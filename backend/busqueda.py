import unicodedata
import re

# Diccionario bidireccional de sinónimos para suplementación deportiva
SINONIMOS = {
    "proteina": ["protein", "proteina", "whey", "isolate", "aislado", "casein", "caseina"],
    "proteinas": ["protein", "proteina", "whey", "isolate", "aislado"],
    "prote": ["protein", "proteina", "whey"],
    "protein": ["protein", "proteina", "whey"],
    "whey": ["whey", "protein", "proteina"],
    "creatina": ["creatine", "creatina", "creapure", "monohidrato"],
    "creatine": ["creatine", "creatina", "creapure"],
    "creapur": ["creapure", "creatine", "creatina"],
    "creapure": ["creapure", "creatine", "creatina"],
    "aminoacidos": ["amino", "bcaa", "eaa", "aminoacidos", "aminoácidos"],
    "amino": ["amino", "bcaa", "eaa"],
    "bcaa": ["bcaa", "amino", "aminoacidos"],
    "cacahuete": ["peanut", "cacahuete", "mani"],
    "avena": ["oat", "oats", "oatmeal", "avena"],
    "harina": ["flour", "harina", "oat"],
    "cafeina": ["caffeine", "cafeina", "cafeína"],
    "glutamina": ["glutamine", "glutamina"],
    "termogenico": ["termogenico", "quemador", "fat burner", "burner"]
}

def normalizar_texto(texto: str) -> str:
    """Elimina acentos, caracteres especiales y convierte a minúsculas."""
    if not texto:
        return ""
    texto_norm = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return re.sub(r'[^a-zA-Z0-9\s]', ' ', texto_norm).lower().strip()

def expandir_terminos_busqueda(query_str: str) -> list:
    """
    Toma la búsqueda del usuario (ej: 'proteina hsn'), la normaliza,
    la divide en tokens y expande cada token con sus sinónimos.
    """
    texto_limpio = normalizar_texto(query_str)
    if not texto_limpio:
        return []

    tokens = texto_limpio.split()
    grupos_terminos = []

    for t in tokens:
        variantes = {t}
        # Si el token o un prefijo coincide con el diccionario de sinónimos
        if t in SINONIMOS:
            variantes.update(SINONIMOS[t])
        else:
            for clave, sinonimos in SINONIMOS.items():
                if t.startswith(clave) or clave.startswith(t):
                    variantes.update(sinonimos)
                    variantes.add(clave)
        grupos_terminos.append(list(variantes))

    return grupos_terminos
