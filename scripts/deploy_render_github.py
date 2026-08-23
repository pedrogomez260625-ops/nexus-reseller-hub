import os
import sys
import io
import json
import urllib.request
import urllib.error
import subprocess

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
DATOS_DIR = os.path.join(os.path.dirname(PARENT_DIR), "datos-ghost-reseller-hub")
CUENTAS_FILE = os.path.join(DATOS_DIR, "cuentas- 0032-ghost-reseller-hub.txt")

GITHUB_USER = "pedrogomez260625-ops"
GITHUB_TOKEN = ""
RENDER_API_KEY = ""
OWNER_ID = "tea-da52pjrm8hqs73b8nvig"
REPO_NAME = "nexus-reseller-hub"

if os.path.exists(CUENTAS_FILE):
    with open(CUENTAS_FILE, "r", encoding="utf-8", errors="ignore") as f:
        for line in f.read().splitlines():
            line = line.strip()
            if line.startswith("ghp_"):
                GITHUB_TOKEN = line
            elif line.startswith("rnd_"):
                RENDER_API_KEY = line

def create_render_web_service():
    print("🔹 Creando Web Service en Render API...")
    headers = {
        "Authorization": f"Bearer {RENDER_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "type": "web_service",
        "name": "nexus-reseller-hub",
        "ownerId": OWNER_ID,
        "repo": f"https://github.com/{GITHUB_USER}/{REPO_NAME}",
        "branch": "main",
        "autoDeploy": "yes",
        "serviceDetails": {
            "env": "python",
            "region": "oregon",
            "plan": "free",
            "envSpecificDetails": {
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT"
            },
            "envVars": [
                {"key": "TELEGRAM_BOT_TOKEN", "value": "YOUR_TELEGRAM_BOT_TOKEN"},
                {"key": "RESELLER_API_KEY", "value": "YOUR_BUNNY_API_KEY"},
                {"key": "ADMIN_TELEGRAM_ID", "value": "1849945160"},
                {"key": "DEPOSIT_WALLET_BSC", "value": "0xec0183f1411c106afb8cfe32c391fef536f681d4"},
                {"key": "DEPOSIT_WALLET_TRON", "value": "TKuRmAYaCQR3nTv3M8XtRZ8VwXfuLHWPbE"}
            ]
        }
    }

    req = urllib.request.Request("https://api.render.com/v1/services", data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            svc = data.get("service", {})
            print("🎉 ¡SERVICIO CREADO CON ÉXITO EN RENDER!")
            print("ID:", svc.get("id"))
            print("Nombre:", svc.get("name"))
            print("URL:", svc.get("serviceDetails", {}).get("url") or f"https://{svc.get('slug')}.onrender.com")
            return data
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(f"Respuesta Render HTTP {e.code}: {err_body}")
        return None
    except Exception as e:
        print(f"Error Render: {e}")
        return None

if __name__ == "__main__":
    create_render_web_service()
