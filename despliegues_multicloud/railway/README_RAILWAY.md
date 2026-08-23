# 🚂 GUÍA DE DESPLIEGUE EN RAILWAY ($0 CON CRÉDITOS MENSUALES)
### Despliegue Instantáneo desde GitHub Repo en 1 Clic

---

## 📋 Pasos para Desplegar en Railway:

1. **Iniciar Sesión:**
   - Entra a [https://railway.app/](https://railway.app/) e inicia sesión con tu cuenta de GitHub (`pedrogomez260625-ops`).

2. **Crear Proyecto desde GitHub:**
   - Haz clic en **New Project** ➔ **Deploy from GitHub repo**.
   - Selecciona el repositorio: `pedrogomez260625-ops/nexus-reseller-hub`.

3. **Configurar Variables de Entorno:**
   - En la pestaña **Variables**, añade:
     * `BOT_TOKEN_NEXUS`: `8873710791:...`
     * `BOT_TOKEN_NOVA`: `8870399329:...`
     * `RESELLER_API_KEY`: `bai_sk_...`
     * `ADMIN_TELEGRAM_ID`: `1849945160`

4. **Generar Dominio Público:**
   - En **Settings** ➔ **Networking** ➔ Haz clic en **Generate Domain**.
   - Te dará una URL pública tipo `nexus-reseller-hub-production.up.railway.app`.

5. **¡Listo!** Railway compilará automáticamente con Nixpacks/Python y activará el Tetra-Hub 24/7.
