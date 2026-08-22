"""
TEST INTERACTIVO EN TIEMPO REAL - CLIENTE TELEGRAM & DIAGNOSTICO NEXUS CORE
Autor: Angelus AGI
"""

import os
import sys
import io
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BUNNY_API_KEY = os.getenv("RESELLER_API_KEY", "")
GAS_WEBHOOK_URL = os.getenv("GAS_WEBHOOK_URL", "")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "1849945160"))

def print_separator(title):
    print("\n" + "=" * 60)
    print(f"🔹 {title}")
    print("=" * 60)

def test_telegram_bot_health():
    print_separator("1. ESTADO DE TELEGRAM BOT API (getMe)")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print("✅ Bot detectado exitosamente:", data.get("result", {}).get("username"))
            return data
    except Exception as e:
        print(f"❌ Error en getMe: {e}")
        return None

if __name__ == "__main__":
    test_telegram_bot_health()
