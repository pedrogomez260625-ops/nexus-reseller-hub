# 🛡️ GUÍA DE DESPLIEGUE EN PELLA.APP (100 MB RAM / 5 GB DISK / $0/MES)
### Hosting Linux Gratuito Permanente para `@cybervault_keys_bot`

---

## 📋 Pasos para Desplegar en Pella:

1. **Iniciar Sesión:**
   - Entra a [https://www.pella.app/home](https://www.pella.app/home).
   - Credenciales: `pedrogomez260625@proton.me` | `234561ASDfg@234`.

2. **Crear Servidor / App:**
   - Haz clic en **Create Server** o **New App**.
   - Elige el plan **Free ($0/month - 100 MB RAM)**.
   - Selecciona el entorno **Python**.

3. **Subir los Archivos:**
   - Ve a la sección **Files / File Manager**.
   - Sube los 3 archivos de la carpeta [`despliegues_multicloud/pella/`](file:///C:/Users/rafae/.gemini/01_PROYECTOS/planes_jules_2026/0032-ghost-reseller-hub/despliegues_multicloud/pella/):
     * `app_pella.py` (Script ultra-liviano con Python estándar, consume **<18 MB RAM**).
     * `Procfile`
     * `requirements.txt`

4. **Variables de Entorno (Environment Variables):**
   - En la sección **Environment / Variables**, añade:
     * `TELEGRAM_BOT_TOKEN`: `8853535007:AAF6Gm9ap4P11e1I9UAHYiPg8gcyEAQEe8M`
     * `RESELLER_API_KEY`: `bai_sk_4a557cbb3c136090682510a41a13585560feff74e56eaa0e`
     * `ADMIN_TELEGRAM_ID`: `1849945160`

5. **Iniciar el Servidor:**
   - Haz clic en el botón verde **Start / Run**.
   - `app_pella.py` iniciará el bucle de polling y el healthcheck HTTP en segundo plano.

¡Listo! `@cybervault_keys_bot` queda atendiendo y despachando licencias en Pella.
