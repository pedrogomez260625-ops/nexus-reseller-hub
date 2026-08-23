"""
=============================================================================
HUGGING FACE SPACES - STEALTH BOOTLOADER / LAUNCHER (PUBLIC REPO)
Este es el único archivo visible públicamente en el Space.
Descarga en memoria el motor privado desde el Dataset Seguro usando HF_TOKEN.
=============================================================================
"""

import os
import sys
import time
import importlib.util
from huggingface_hub import hf_hub_download

# Variables de entorno inyectadas desde los Secrets del Space
HF_TOKEN = os.getenv("HF_TOKEN")
DATASET_REPO = os.getenv("DATASET_REPO", "pedrogomez260625/reseller-core-vault")
CORE_FILENAME = os.getenv("CORE_FILENAME", "bot_core.py")

print("=" * 60)
print("🚀 [STEALTH LAUNCHER] Inicializando entorno seguro...")
print(f"📦 Repositorio Seguro: {DATASET_REPO}")
print(f"🔑 Autenticación HF Token: {'Presente' if HF_TOKEN else 'FALTANTE'}")
print("=" * 60)

if not HF_TOKEN:
    print("⚠️ ADVERTENCIA: HF_TOKEN no fue configurado en Settings > Secrets.")

try:
    print(f"⏳ Descargando motor de ejecución privado ({CORE_FILENAME})...")
    local_path = hf_hub_download(
        repo_id=DATASET_REPO,
        filename=CORE_FILENAME,
        repo_type="dataset",
        token=HF_TOKEN
    )
    print(f"✅ Motor descargado en memoria temporal: {local_path}")

    # Carga e importación dinámica del módulo protegido
    spec = importlib.util.spec_from_file_location("bot_core", local_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"No se pudo cargar el módulo desde {local_path}")

    bot_module = importlib.util.module_from_spec(spec)
    sys.modules["bot_core"] = bot_module
    spec.loader.exec_module(bot_module)

    # Exponer la aplicación FastAPI
    app = getattr(bot_module, "app", None)
    if app is None:
        raise AttributeError("No se encontró la instancia 'app' de FastAPI en el módulo importado.")

    print("🌟 [STEALTH LAUNCHER] Motor ejecutándose exitosamente.")

except Exception as err:
    print(f"❌ ERROR CRÍTICO cargando motor privado: {err}")
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse

    app = FastAPI(title="Maintenance Mode")

    @app.get("/", response_class=HTMLResponse)
    async def maintenance():
        return """
        <html>
            <head><title>System Initializing</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px; background: #0f172a; color: white;">
                <h2>⚙️ Service Initializing</h2>
                <p>Configuring secure runtime components...</p>
            </body>
        </html>
        """

    @app.get("/health")
    async def health():
        return {"status": "initializing", "error": str(err)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)
