# AGENTS.md - System & Privacy Directives

## 🛡️ ANONYMITY & IDENTITY SHIELDING (CRITICAL RULE)
1. **Zero Personal Attribution**: This repository MUST NEVER contain real personal names, private home disk paths, DNI, personal emails, or clinical identities in code, docstrings, commits, or web responses.
2. **System Name**: Always reference the project as `Nexus Reseller Core` or `Ghost Reseller System`.
3. **Traceback Sanitization**: FastAPI endpoints must handle top-level exceptions cleanly without leaking local file paths or raw stack traces.
4. **Environment Isolation**: Secret API keys (`RESELLER_API_KEY`, `CRYPTO_BOT_TOKEN`, `TELEGRAM_BOT_TOKEN`) must only be read from `.env` and NEVER hardcoded or committed to git.

## 📦 Project Architecture
- `src/ghost_reseller/config.py`: Anonymous settings module.
- `src/ghost_reseller/main.py`: FastAPI server for webhooks & health checks.
- `src/ghost_reseller/services/supplier_client.py`: Upstream API client for product catalog and instant order fulfillment.
- `src/ghost_reseller/services/wallet_ledger.py`: Isolated USDT balance and transaction history manager.
- `tests/`: Automated unit test suite using `pytest`.



### 🧬 RADAR DE INVESTIGACIÓN SOTA GEMINI SPARK (EN VIVO EN GOOGLE DRIVE):
Gemini Spark está ejecutando misiones de investigación semanales (PubMed, arXiv, SOTA) y depositando documentos ejecutivos en las carpetas de Google Drive de este ecosistema.
- **Acción Obligatoria para Jules:** Al iniciar tu sesión, corre `python scripts/gdrive_hub.py --list` para verificar si hay nuevos reportes científicos (ej: `REPORTE_SOTA_MAMOGRAFIA_LUNES.docx`, `REPORTE_GNN_FARMACOLOGIA.docx`, `DEFENSA_Y_CRIPTO_REPORTE.docx`).
- **Asimilación:** Utiliza las fórmulas, hiperparámetros y sugerencias teóricas de esos reportes para guiar el desarrollo de tus módulos en `src/` y tests en `tests/`.

## 📡 6. TELEMETRÍA GOOGLE SHEETS & ALMACENAMIENTO GOOGLE DRIVE
Todo agente autónomo en este repositorio cuenta con conexión al Google Workspace del ecosistema:
- **Tablero Maestro:** Consulta y telemetría en [📊 Angelus - Ecosistema Maestro 2026](https://docs.google.com/spreadsheets/d/1yS-sqml_7OuFN6vrIeP3LcDFa1bgXuxpefG4BSCzwwE/edit).
- **Google Drive Dedicado:** Tu repositorio tiene una carpeta asignada en `🏛️ Ecosistema_Angelus_2026/`.
- **Herramienta Integrada `scripts/gdrive_hub.py`:**
  - Reportar telemetría y tests: `python scripts/gdrive_hub.py --status "🟢 Tests OK" --task "Próxima tarea" --notes "Resumen"`
  - Subir libros KDP, PDFs, datasets o pesos: `python scripts/gdrive_hub.py --upload "ruta/al/archivo"`
  - Listar archivos en Drive: `python scripts/gdrive_hub.py --list`
