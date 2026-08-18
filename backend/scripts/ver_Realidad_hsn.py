import requests

url = "https://www.hsnstore.com/marcas/essential-series/sulforafano-de-brocoli-10mg-200mg-sulfodyne"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9'
}

print("Pidiendo la web a HSN...")
res = requests.get(url, headers=headers)

with open("hsn_captura.html", "w", encoding="utf-8") as f:
    f.write(res.text)

print(f"Estado devuelto: {res.status_code}")
print("✅ Archivo 'hsn_captura.html' guardado.")