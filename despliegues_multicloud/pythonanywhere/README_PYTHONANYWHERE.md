# 🐍 GUÍA DE DESPLIEGUE EN PYTHONANYWHERE ($0/MES)
### Hosting Web Python 24/7 Permanente en `usuario.pythonanywhere.com`

---

## 📋 Pasos para Desplegar en PythonAnywhere (2 Minutos):

1. **Crear Cuenta Gratuita:**
   - Entra a [https://www.pythonanywhere.com/](https://www.pythonanywhere.com/) y crea una cuenta gratuita (*Beginner account*, $0).
   - Tu subdominio será: `tu_usuario.pythonanywhere.com`.

2. **Crear la Web App:**
   - Ve a la pestaña **Web** (arriba).
   - Haz clic en **Add a new web app**.
   - Selecciona **Manual configuration** (o **Flask**) ➔ Elige **Python 3.10** o **Python 3.11**.

3. **Subir o Pegar el Código:**
   - Ve a la pestaña **Files** ➔ `mysite/` (o el directorio de tu app).
   - Abre `flask_app.py` (o sube el archivo de esta carpeta).
   - Pega el código de [`despliegues_multicloud/pythonanywhere/flask_app.py`](file:///C:/Users/rafae/.gemini/01_PROYECTOS/planes_jules_2026/0032-ghost-reseller-hub/despliegues_multicloud/pythonanywhere/flask_app.py).
   - Guarda el archivo.

4. **Recargar la Web App:**
   - Vuelve a la pestaña **Web**.
   - Haz clic en el botón verde grande: **`Reload <tu_usuario>.pythonanywhere.com`**.

5. **Configurar el Webhook de Telegram:**
   - Abre tu navegador o ejecuta una petición para vincular tu bot a PythonAnywhere:
     ```text
     https://api.telegram.org/bot8870399329:AAG9Co0upODc7UJ_QgodmgaQiORNPc9jTX4/setWebhook?url=https://<tu_usuario>.pythonanywhere.com/webhook
     ```
   - Telegram responderá: `{"ok": true, "result": true, "description": "Webhook was set"}`.

¡Listo! El bot responderá 24/7 sin límites de tiempo en PythonAnywhere.
