# 📄 GUÍA MAESTRA PASO A PASO: PROYECTO NEXUS RESELLER CORE (0032)
### Sistema Anónimo de Reventa Digital & Pasarela Cripto en Telegram
**Proyecto:** `0032-ghost-reseller-hub`  
**Identidad del Sistema:** `Nexus Reseller Core`  
**Nivel de Seguridad:** Blindaje de Privacidad y Anonimato Total (Aislamiento de Entidades Oficiales e Infraestructuras Sensibles)

---

## 📌 ÍNDICE DE PASOS

1. [Paso 1: Creación de la Identidad Neutra y Correo Anónimo](#paso-1-creación-de-la-identidad-neutra-y-correo-anónimo)
2. [Paso 2: Creación del Bot de Telegram en @BotFather](#paso-2-creación-del-bot-de-telegram-en-botfather)
3. [Paso 3: Obtención de la API Key de Bunny AI Tools (Proveedor)](#paso-3-obtención-de-la-api-key-de-bunny-ai-tools-proveedor)
4. [Paso 4: Despliegue de la Base de Datos Gratuita en Google Apps Script (GAS)](#paso-4-despliegue-de-la-base-de-datos-gratuita-en-google-apps-script-gas)
5. [Paso 5: Despliegue del Bot en Hosting Gratuito (Pella / TeleBotHost / FPS.MS)](#paso-5-despliegue-del-bot-en-hosting-gratuito-pella--telebothost--fpsms)
6. [Paso 6: Configuración de la Billetera Cripto (MetaMask / @CryptoBot)](#paso-6-configuración-de-la-billetera-cripto-metamask--cryptobot)
7. [Paso 7: Prueba de Funcionamiento 1-Clic](#paso-7-prueba-de-funcionamiento-1-clic)

---

## 🔐 PASO 1: CREACIÓN DE LA IDENTIDAD NEUTRA Y CORREO ANÓNIMO (✅ COMPLETADO)

**Estado:** 🟢 COMPLETADO CON ÉXITO EL 17 DE AGOSTO DE 2026

1. **Correo Anónimo ProtonMail Creado:** `tu_correo_anonimo@proton.me`
2. **Cuenta de Google Asociada para GAS ($0 DB):** Registrada cuenta Google independiente con `tu_correo_anonimo@proton.me` para acceso a Google Apps Script.
3. **Custodia de Credenciales:** Frase de recuperación y contraseñas respaldadas.

---

## 🤖 PASO 2: CREACIÓN DEL BOT DE TELEGRAM EN @BOTFATHER (EN PROGRESO / CUENTA VIEJA)

**Nota de Seguridad sobre Cuenta / Número de Telegram:**
- Se puede utilizar una cuenta de Telegram existente o un número viejo para ingresar a `@BotFather`.
- **Independencia del Bot:** El Bot opera exclusivamente con su **API Bot Token**. Si la cuenta o el número SIM se inhabilitan en el futuro, **el bot sigue VIVO 24/7 y no se pierden fondos, código ni datos** (los fondos residen en MetaMask/EVM y los datos en Google Apps Script).
- **Transferencia Futura:** En cualquier momento se puede ejecutar `/transfer` en `@BotFather` para migrar la propiedad del bot a una nueva cuenta de Telegram.

El bot de Telegram se crea a través del sistema oficial de Telegram (`@BotFather`). Esto genera un **Bot Token aislado** que **NO expone tu número SIM personal**:

1. En Telegram, busca el usuario verificado **`@BotFather`**.
2. Envía el comando: `/newbot`.
3. Ingrese un nombre visible para el bot (ejemplo: `Nexus Premium Keys Bot` o `Digital AI Store`).
4. Ingrese un usuario terminado en `bot` (ejemplo: `nexus_digital_store_bot`).
5. `@BotFather` te responderá entregándote el **API Token del Bot**.
   - *Formato:* `7123456789:AAE-xxxxxxxxx_xxxxxxxxx`
6. Copia y guarda este Token en un bloc de notas seguro.

---

## 📦 PASO 3: OBTENCIÓN DE LA API KEY DE BUNNY AI TOOLS (PROVEEDOR)

Esta API Key te permite consultar el catálogo de productos mayoristas a precio de costo ($1.00 USDT) y comprar las licencias en 1 segundo:

1. Abre el bot mayorista en Telegram: **`@bunnytoolss_bot`**.
2. Presiona en el menú principal: **`🔑 My API Key`**.
3. El bot te devolverá tu clave de revendedor API.
   - *Formato:* `bai_sk_xxxxxxxxxxxxxxxxxxxxxxxx`
4. Copia tu clave API de Bunny.
5. *(Opcional)* En el menú del bot presiona **`Deposit`** para recargar $2 o $5 USDT cuando estés listo para comenzar las ventas.

---

## 📊 PASO 4: DESPLIEGUE DE LA BASE DE DATOS GRATUITA EN GOOGLE APPS SCRIPT (GAS)

Google Apps Script funciona como una **base de datos web de clave-valor 100% gratuita e invisible** para guardar saldos en USDT e historial de clientes:

1. Entra a [Google Apps Script](https://script.google.com/) con tu correo anónimo de Google/Proton.
2. Haz clic en **`Nuevo proyecto`**.
3. Borra todo el código por defecto y copia íntegramente el contenido del archivo de nuestro proyecto:  
   [`0032-ghost-reseller-hub/gas_script/Code.gs`](./gas_script/Code.gs)
4. Haz clic en **`Implementar`** -> **`Nueva implementación`**.
5. Selecciona el icono de engranaje ⚙️ -> **`Aplicación web`**.
   - **Descripción:** `Nexus GAS DB`
   - **Ejecutar como:** `Yo (tu correo anónimo)`
   - **Quién tiene acceso:** `Cualquier persona` (*Anyone*)
6. Haz clic en **`Implementar`** y autoriza los permisos.
7. Copia la **URL de la aplicación web**.
   - *Formato:* `https://script.google.com/macros/s/AKfycbx.../exec`

---

## ☁️ PASO 5: DESPLIEGUE DEL BOT EN HOSTING GRATUITO (PELLA / TELEBOTHOST / FPS.MS)

Para que el bot responda 24/7 sin instalar nada en tu PC ni usar servidores institucionales o personales:

### Opción A: Pella / TeleBotHost
1. Entra a [Pella App](https://pella.app/) o [TeleBotHost](https://telebothost.com/).
2. Regístrate con tu correo anónimo (sin tarjeta de crédito).
3. Selecciona **`Create New Bot`** o **`Add Bot Token`**.
4. Pega el Token de `@BotFather` que obtuviste en el Paso 2.
5. Pega el código de Python del bot o conecta el repositorio de GitHub.
6. El hosting mantendrá el bot **ONLINE 24/7**.

### Opción B: FPS.MS
1. Entra a [FPS.MS Free Telegram Bot Hosting](https://fps.ms/free-telegram-bot-hosting/).
2. Crea tu cuenta gratuita y sube la carpeta `src/ghost_reseller`.
3. Inicia el proceso en 1-clic.

---

## 💳 PASO 6: CONFIGURACIÓN DE LA BILLETERA CRIPTO (METAMASK / @CRYPTOBOT)

Para cobrar las criptos (USDT / TON / BNB) de los clientes:

### Método 1: Billetera Anónima MetaMask (EVM)
1. Instala la extensión de **MetaMask** en un navegador limpio.
2. Crea una billetera anónima de red Polygon / BSC (Binance Smart Chain).
3. Copia tu dirección pública de depósito (ejemplo: `0x1234...5678`).
4. Los clientes transfieren USDT en Polygon/BSC a esta dirección.

### Método 2: API Oficial de @CryptoBot
1. En Telegram entra al bot oficial **`@CryptoBot`**.
2. Ve a `/pay` -> **`Create App`** para obtener tu `CRYPTO_BOT_TOKEN`.
3. Permite generar cobros automáticos en USDT/TON con notificación instantánea.

---

## ⚡ PASO 7: PRUEBA DE FUNCIONAMIENTO 1-CLIC

Una vez completados los pasos, el flujo comercial automático opera así:

1. **El cliente entra a tu Bot de Telegram:** Presiona `/start` y ve el catálogo con tus precios ($4.00 USDT por Gemini Pro 18 meses).
2. **El cliente deposita $4.00 USDT:** Vía `@CryptoBot` o transferencia MetaMask.
3. **El bot valida el saldo:** Acredita $4.00 USDT en la base de datos de Google Apps Script.
4. **El bot compra en 1 segundo:** Invoca a `POST /order` en Bunny AI Tools consumiendo $1.00 USDT de tu saldo mayorista.
5. **Entrega instantánea:** El bot le entrega al cliente en el chat la clave/cuenta entregada (`delivered[0]`).
6. **Tu Ganancia Netas ($3.00 USDT):** Quedan acreditados limpiamente en tu billetera.

---

### 🛡️ REGISTRO DE SEGURIDAD
- Repositorio local preparado: `./0032-ghost-reseller-hub`
- Cero nombres reales. Cero correlación con entidades oficiales o académicas. Cero infraestructura personal.
