# ⚙️ GUÍA DE CONFIGURACIÓN DE TAREAS PROGRAMADAS EN JULES WEB UI
### Proyecto: `0032-ghost-reseller-hub` - Ghost Reseller Hub - Anonymous Telegram Reseller System
**Investigador Principal:** Perez, Ernesto Rafael ("Rafa") & Angelus AGI

---

## 🎯 DOMINIO Y MISIÓN DEL PROYECTO
> **Área Objetivo:** Sistema anónimo de reventa digital automatizado en Telegram, pasarela de pago cripto USDT/MetaMask y base de datos $0 en Google Apps Script.  
> **Módulos Principales:** `src/ghost_reseller/config.py, main.py, services/supplier_client.py, gas_script/Code.gs`

---

## 💡 CÓMO CONFIGURAR LAS 3 TAREAS PROGRAMADAS EN LA INTERFAZ WEB DE JULES
> **Instrucción para Rafa:** En el menú web de Jules (`Configure Repo -> Scheduled Task`), crea **únicamente 3 Tareas Programadas fijas**. Copia y pega los siguientes 3 prompts adaptados a este repositorio. **NUNCA tendrás que cambiarlos en la web**, porque Jules reescribirá autónomamente su propio archivo `JULES_DYNAMIC_TASKS.md` en GitHub al concluir cada día.

---

### 🟢 TAREA PROGRAMADA 1 DE 3 (INICIO DE DÍA, LECTURA DE MEMORIA Y LOG DE EJECUCIÓN)
- **Frecuencia:** Diaria (Ej: 09:00 AM)
- **Prompt a copiar en el menú web:**
> "Hola Jules. Iniciamos el ciclo diario de auto-evolución en el proyecto `0032-ghost-reseller-hub` (Ghost Reseller Hub - Anonymous Telegram Reseller System) para **Perez, Ernesto Rafael**.
> 
> Pasos de Inicialización y Memoria:
> 1. Abre y lee `ARQUITECTURA_ESTADO.md` y `JULES_DYNAMIC_TASKS.md` para conocer el estado del código e inventario.
> 2. Revisa `JULES_EXECUTION_LOG.md`. Si la sesión anterior terminó con algún error o tarea incompleta, toma nota del fallo para corregirlo prioritariamente.
> 3. Si `JULES_DYNAMIC_TASKS.md` no existe o está vacío, créalo analizando los módulos en disco (`src/ghost_reseller/config.py, main.py, services/supplier_client.py, gas_script/Code.gs`).
> 4. Ejecuta `pytest tests/` para validar el estado de partida del repositorio.
> 5. Firma de autoría: `Perez, Ernesto Rafael ("Rafa")`."

---

### ⚡ TAREA PROGRAMADA 2 DE 3 (EJECUCIÓN INTERMEDIA & REGLAS DE DOMINIO)
- **Frecuencia:** Diaria (Ej: 14:00 PM)
- **Prompt a copiar en el menú web:**
> "Hola Jules. Continuamos con el desarrollo autónomo en `0032-ghost-reseller-hub` (Ghost Reseller Hub - Anonymous Telegram Reseller System) para **Perez, Ernesto Rafael**.
> 
> Pasos de Ejecución Intermedia:
> 1. Consulta las 6 reglas de arquitectura en `JULES_ARCHITECTURE_RULES.md` y las tareas dinámicas en `JULES_DYNAMIC_TASKS.md`.
> 2. Ejecuta las tareas enfocadas en la misión principal del proyecto: Sistema anónimo de reventa digital automatizado en Telegram, pasarela de pago cripto USDT/MetaMask y base de datos $0 en Google Apps Script..
> 3. Refactoriza e incrementa los módulos principales (`src/ghost_reseller/config.py, main.py, services/supplier_client.py, gas_script/Code.gs`) sin romper funcionalidades previas, asegurando resiliencia en los 5 Servidores MCP (`Render`, `Stitch`, `v0`, `Supabase`, `Context7`) de `AGENTS.md`.
> 4. Corre `pytest tests/` y confirma pasaje al 100%. En caso de error, no te detengas; registra el diagnóstico parcial en `JULES_EXECUTION_LOG.md` y aplica la recuperación.
> 5. Firma de autoría: `Perez, Ernesto Rafael ("Rafa")`."

---

### 🛑 TAREA PROGRAMADA 3 DE 3 (CIERRE, REGISTRO DE LOGS Y REESCRITURA AUTÓNOMA)
- **Frecuencia:** Diaria (Ej: 20:00 PM)
- **Prompt a copiar en el menú web:**
> "Hola Jules. Sesión final de cierre y auto-evolución en `0032-ghost-reseller-hub` para **Perez, Ernesto Rafael**.
> 
> Pasos de Cierre, Registro de Log y Reescritura Autónoma:
> 1. Ejecuta la suite de pruebas con `pytest tests/` y documenta el resultado de la sesión.
> 2. **REGISTRO DE LOG DE EJECUCIÓN:** Registra una entrada en `JULES_EXECUTION_LOG.md` anotando la fecha, tareas completadas, pruebas pasadas y cualquier fallo o advertencia detectada con su plan de remediación.
> 3. Actualiza `ARQUITECTURA_ESTADO.md` registrando la lista de módulos actualizados y el diff de arquitectura de hoy.
> 4. **AUTO-REESCRITURA DINÁMICA:** Evalúa los requerimientos futuros de Ghost Reseller Hub - Anonymous Telegram Reseller System, **Y REESCRIBE TOTALMENTE `JULES_DYNAMIC_TASKS.md` grabando entre 5 y 10 nuevas super-tareas autónomas para la sesión de mañana.**
> 5. Firma de autoría: `Perez, Ernesto Rafael ("Rafa")`."

---
[VINCIT_OMNIA_VERITAS]
