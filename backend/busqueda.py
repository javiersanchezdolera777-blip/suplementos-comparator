import unicodedata
import re

# Diccionario bidireccional exhaustivo (con y sin tildes, ES y EN)
SINONIMOS = {
    "proteina": ["protein", "proteina", "proteína", "proteinas", "proteínas", "whey", "isolate", "aislado", "casein", "caseina", "caseína"],
    "prote": ["protein", "proteina", "proteína", "whey", "isolate", "aislado"],
    "protein": ["protein", "proteina", "proteína", "whey", "isolate", "aislado"],
    "whey": ["whey", "protein", "proteina", "proteína", "suero"],
    "creatina": ["creatine", "creatina", "creatína", "creapure", "monohidrato"],
    "creatine": ["creatine", "creatina", "creatína", "creapure"],
    "creapur": ["creapure", "creatine", "creatina", "creatína"],
    "creapure": ["creapure", "creatine", "creatina", "creatína"],
    "aminoacidos": ["amino", "bcaa", "eaa", "aminoacidos", "aminoácidos"],
    "amino": ["amino", "bcaa", "eaa", "aminoacidos", "aminoácidos"],
    "bcaa": ["bcaa", "amino", "aminoacidos", "aminoácidos"],
    "cacahuete": ["peanut", "cacahuete", "cacahuates", "mani"],
    "avena": ["oat", "oats", "oatmeal", "avena"],
    "harina": ["flour", "harina", "oat", "avena"],
    "cafeina": ["caffeine", "cafeina", "cafeína"],
    "glutamina": ["glutamine", "glutamina"],
    "termogenico": ["termogenico", "termogénico", "quemador", "fat burner", "burner"]
}

def normalizar_palabra_base(texto: str) -> str:
    """Elimina acentos y caracteres especiales para buscar en el diccionario."""
    if not texto:
        return ""
    texto_norm = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return re.sub(r'[^a-zA-Z0-9]', '', texto_norm).lower().strip()

def expandir_terminos_busqueda(query_str: str) -> list:
    """
    Toma la búsqueda del usuario (ej: 'proteina hsn'),
    extrae cada palabra y devuelve los grupos de sinónimos con y sin tilde.
    """
    if not query_str:
        return []

    palabras = query_str.strip().split()
    grupos_terminos = []

    for pal in palabras:
        base = normalizar_palabra_base(pal)
        if not base:
            continue

        variantes = {pal, base}

        # Comprobar coincidencia directa o por prefijo en el diccionario
        if base in SINONIMOS:
            variantes.update(SINONIMOS[base])
        else:
            for clave, sinonimos in SINONIMOS.items():
                if base.startswith(clave) or clave.startswith(base):
                    variantes.update(sinonimos)
                    variantes.add(clave)

        grupos_terminos.append(list(variantes))

    return grupos_terminos
