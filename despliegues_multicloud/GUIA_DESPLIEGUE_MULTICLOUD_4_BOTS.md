# 🌐 GUÍA MAESTRA DE DESPLIEGUE MULTI-CLOUD: 4 BOTS EN 4 PLATAFORMAS GRATUITAS ($0/MES)
### Ecosistema Reseller Soberano — Nexus / Nova / DevCore / CyberVault
**Identidad Operativa:** `pedrogomez260625-ops` | `pedrogomez260625@proton.me`

---

## 🗺️ 1. MAPA DE INFRAESTRUCTURA Y ASIGNACIÓN DE BOTS

| Bot | Token Telegram | Plataforma Cloud | Hardware Gratuito | Estado |
| :--- | :--- | :--- | :--- | :---: |
| **1. `@nexus_ai_store_bot`** | `8873710791:AAEKE...` | **Render Cloud** | 512 MB RAM / FastAPI + Webhook | 🟢 **LIVE** |
| **2. `@nova_ai_keys_bot`** | `8870399329:AAG9C...` | **Hugging Face Spaces** | **16 GB RAM / 2 vCPU** (Docker FastAPI) | ⚡ Listo para Subir |
| **3. `@devcore_pro_bot`** | `8918777311:AAFXq...` | **TeleBotHost** | Ilimitado / Específico para Bots | ⚡ Listo para Subir |
| **4. `@cybervault_keys_bot`** | `8853535007:AAF6G...` | **Pella.app** | 100 MB RAM / 5 GB Disk / Python | ⚡ Listo para Subir |
| *(Respaldo Total 24/7)* | *(Todos)* | **Google Apps Script** | Serverless / 0ms cold-start | ✅ Configurado |

---

## ⚡ 2. ¿SIRVE HUGGING FACE SPACES COMO ALTERNATIVA? (¡ES EXCELENTE!)

### 🚀 Ventajas de Hugging Face Spaces:
- **16 GB de RAM y 2 vCPUs GRATIS** (32 veces más memoria que Render).
- **Soporte Docker & FastAPI nativo:** Ejecuta el backend completo y escucha Webhooks en el puerto `7860`.
- **URL Pública Inmediata:** `https://<tu-usuario>-nova-reseller-hub.hf.space/`
- **Secretos Protegidos:** Puedes agregar `BOT_TOKEN` y `RESELLER_API_KEY` en los *Settings > Secrets* de Hugging Face sin exponerlos en el código.
- **¿Cómo evitar que se duerma?**
  - Con un simple ping HTTP periódico desde GitHub Actions (`despertador-servicios`) o el mismo webhook de Telegram al recibir mensajes.

### 📦 Pasos para Crear el Space en Hugging Face (2 minutos):
1. Entra a [HuggingFace.co](https://huggingface.co/) con tu cuenta (`pedrogomez260625` o la que prefieras).
2. Haz clic en **New Space**:
   - **Space Name:** `nova-ai-keys-hub`
   - **License:** `mit` o `apache-2.0`
   - **Select Space SDK:** Elige **Docker** (Blank)
   - **Space Hardware:** Free (2 vCPU - 16 GB RAM)
   - **Visibility:** `Public` (para que el Webhook de Telegram funcione directo).
3. Sube los 4 archivos ubicados en `despliegues_multicloud/huggingface/`:
   - `Dockerfile`
   - `app.py`
   - `requirements.txt`
   - `README.md`
4. En **Settings > Variables and secrets**, agrega:
   - `TELEGRAM_BOT_TOKEN`: `8870399329:AAG9Co0upODc7UJ_QgodmgaQiORNPc9jTX4`
   - `RESELLER_API_KEY`: `bai_sk_4a557cbb3c136090682510a41a13585560feff74e56eaa0e`
   - `ADMIN_TELEGRAM_ID`: `1849945160`
5. ¡Listo! El Space compila en 30 segundos y `@nova_ai_keys_bot` queda 100% activo 24/7.

---

## 🤖 3. DESPLIEGUE EN TELEBOTHOST (`console.telebothost.com`)

### 📋 Características:
- Cuenta: `pedrogomez260625@proton.me` | `234561ASDfg@234`
- Diseñado exclusivamente para Telegram Bots con consola visual en tiempo real.

### 📦 Pasos de Despliegue:
1. Inicia sesión en [https://console.telebothost.com/](https://console.telebothost.com/).
2. Haz clic en **Create New Bot / Subir Bot**.
3. Sube o pega el contenido de:
   - `despliegues_multicloud/telebothost/bot_telebothost.py`
   - `despliegues_multicloud/telebothost/requirements.txt`
4. Inicia el bot desde el botón **Start**.
5. ¡Listo! `@devcore_pro_bot` queda atendiendo en vivo.

---

## 🛡️ 4. DESPLIEGUE EN PELLA (`pella.app`)

### 📋 Características:
- Cuenta: `pedrogomez260625@proton.me` | `234561ASDfg@234`
- Entorno Linux ultraligero con 100 MB RAM y 5 GB de disco.
- Hemos creado `app_pella.py` con **cero librerías pesadas** (solo Python Standard Library), consumiendo **menos de 18 MB de RAM**.

### 📦 Pasos de Despliegue:
1. Inicia sesión en [https://www.pella.app/home](https://www.pella.app/home).
2. Crea una nueva aplicación **Python**.
3. Sube los archivos de `despliegues_multicloud/pella/`:
   - `app_pella.py`
   - `Procfile`
   - `requirements.txt`
4. Pulsa **Deploy / Run**.
5. ¡Listo! `@cybervault_keys_bot` queda operativo.

---

## 💰 5. RESUMEN DE BILLETERAS DE COBRO CONFIGURADAS EN TODOS LOS BOTS

Todas las plataformas ya tienen inyectadas tus direcciones oficiales de cobro para que el dinero minorista vaya directo a tus billeteras:

- 🟡 **USDT BEP-20 (BNB Smart Chain / MetaMask):** `0xe733e832e20cAE3a1e897F7F4A5B6e16934675C9`
- 🔴 **USDT TRC-20 (Red Tron):** `TZ3DYd7HNhnnSYUfris5Pqm66YmDugQ5Ch`
- 🟣 **Solana (SOL / USDT SPL):** `cjwdWUXMtHgNU4dQmWEKPuyYLm4eonxpfyjhL6crCu4`
- 🟠 **Bitcoin (BTC Nativo):** `bc1qt3s56f8h4crf69httj2snvseq5q6lskpnn5w64`
- 🤖 **Telegram Directo:** `@CryptoBot` y comprobante al admin `@Cctes001`.

---
[VINCIT_OMNIA_VERITAS]
