import os
import sys
import io
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

API_KEY = os.getenv("RESELLER_API_KEY", "")
BASE_URL = os.getenv("RESELLER_BASE_URL", "https://bhao.site/api/reseller/v1")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

req = urllib.request.Request(f"{BASE_URL}/products", headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
    products = data.get("products", [])
    print(f"📦 Total productos en vivo: {len(products)}")
    for p in products:
        print(f"ID {p.get('id'):3d} | Tipo: {p.get('type', 'tools'):8s} | Costo: ${p.get('price_usdt')} | Stock: {str(p.get('stock')):8s} | {p.get('name')}")
except Exception as e:
    print("Error:", e)
