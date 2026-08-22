# 🏛️ REGLAS PERMANENTES DE ARQUITECTURA Y AUDITORÍA DE ERRORES
### Proyecto: `0032-ghost-reseller-hub` - Ghost Reseller Hub - Anonymous Telegram Reseller System
**Investigador Principal:** Perez, Ernesto Rafael ("Rafa") & Angelus AGI

---

## 📌 1. DOMINIO TÉCNICO Y MÓDULOS BASE
- **Misión de Proyecto:** Sistema anónimo de reventa digital automatizado en Telegram, pasarela de pago cripto USDT/MetaMask y base de datos $0 en Google Apps Script.
- **Módulos Core Protegidos:** `src/ghost_reseller/config.py, main.py, services/supplier_client.py, gas_script/Code.gs`

---

## 🛡️ 2. DIRECTIVAS ARQUITECTÓNICAS Y TOLERANCIA A ERRORES
Jules debe aplicar estas 6 reglas de arquitectura en cada sesión:

1. **REGLA 1 (Conservación de Estado):** Nunca sobrescribir código funcional existente. Leer `ARQUITECTURA_ESTADO.md` antes de editar.
2. **REGLA 2 (Recuperación de Errores & Logging):** Si una sesión encuentra un fallo sintáctico, error de red o test roto, Jules NO se detiene en pánico. Registra la traza del error en `JULES_EXECUTION_LOG.md`, aplica una solución temporal o fallback y documenta la remediación.
3. **REGLA 3 (Calidad & Tipado):** Aplicar manejo determinista de excepciones, tipado estricto (`typing` / `Pydantic`) y optimizaciones en `src/ghost_reseller/config.py, main.py, services/supplier_client.py, gas_script/Code.gs`.
4. **REGLA 4 (Conectividad MCP):** Garantizar resiliencia y fallback en los 5 Servidores MCP (`Render Cloud`, `Google Stitch UI`, `Vercel v0`, `Supabase PAT`, `Context7`) definidos en `AGENTS.md`.
5. **REGLA 5 (Telemetría de Salud):** Mantener activo el endpoint `/health` con telemetría de memoria, uptime y estado de dependencias.
6. **REGLA 6 (Cobertura Unit Test & Difusión):** Mantener `pytest` al 100% y redactar capítulos didácticos de avances en `book/` o `docs/`.

---
7. **REGLA 7 (Canal de Comunicación con Angelus & Rafa):** Si Jules requiere credenciales adicionales, servidores de mayor potencia (RAM/OCPU), saldo o guía estratégica superior, debe redactar su petición en `MENSAJES_PARA_ANGELUS.md`. Jules debe entender que Angelus y Rafa leerán este buzón periódicamente (cada par de semanas). **Jules NO DEBE depender ni detenerse a esperar respuesta**; debe continuar trabajando autónomamente mediante fallbacks, pero sabiendo que Angelus le responderá en `RESPUESTAS_DE_ANGELUS.md` cuando revise el canal.

---
[VINCIT_OMNIA_VERITAS]
