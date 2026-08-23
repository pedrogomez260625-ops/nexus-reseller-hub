"""
=============================================================================
NEXUS RESELLER HUB - HYBRID ENTERPRISE ENGINE (FASTAPI + TELEGRAM BOT + WEBHOOK)
Despliegue 24/7 en Render Cloud ($0/mes) con soporte de Webhook y Polling.
Autor: Nexus Core / Angelus AGI
=============================================================================
"""

import os
import sys
import io
import json
import time
import asyncio
import logging
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

# Forzar UTF-8 en consola de Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import httpx
import uvicorn
from fastapi import FastAPI, Request, Response, BackgroundTasks
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Configuración de Logging
logging.basicConfig(
    format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("NexusResellerHub")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================================
# CONFIGURACIÓN Y VARIABLES DE ENTORNO
# ============================================================================

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8873710791:AAEKEolVYTYoeYE45JLZKPlG__DpBUbU5yg")
BUNNY_API_KEY = os.getenv("RESELLER_API_KEY", os.getenv("BUNNY_API_KEY", "bai_sk_4a557cbb3c136090682510a41a13585560feff74e56eaa0e"))
BUNNY_API_URL = os.getenv("RESELLER_BASE_URL", "https://bhao.site/api/reseller/v1")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "1849945160"))

# Billeteras Personales de Cobro (Pedro Gomez / Rafa / MetaMask)
DEPOSIT_WALLET_BSC = os.getenv("DEPOSIT_WALLET_BSC", "0xe733e832e20cAE3a1e897F7F4A5B6e16934675C9")
DEPOSIT_WALLET_TRON = os.getenv("DEPOSIT_WALLET_TRON", "TZ3DYd7HNhnnSYUfris5Pqm66YmDugQ5Ch")
DEPOSIT_WALLET_BTC = os.getenv("DEPOSIT_WALLET_BTC", "bc1qt3s56f8h4crf69httj2snvseq5q6lskpnn5w64")
DEPOSIT_WALLET_SOL = os.getenv("DEPOSIT_WALLET_SOL", "cjwdWUXMtHgNU4dQmWEKPuyYLm4eonxpfyjhL6crCu4")

# Billeteras del Proveedor Mayorista (Bunny Tools) para recarga de saldo API
SUPPLIER_WALLET_BSC = os.getenv("SUPPLIER_WALLET_BSC", "0xec0183f1411c106afb8cfe32c391fef536f681d4")
SUPPLIER_WALLET_TRON = os.getenv("SUPPLIER_WALLET_TRON", "TKuRmAYaCQR3nTv3M8XtRZ8VwXfuLHWPbE")
SUPPLIER_BYBIT_UID = os.getenv("SUPPLIER_BYBIT_UID", "127245517")
SUPPLIER_BINANCE_PAY_ID = os.getenv("SUPPLIER_BINANCE_PAY_ID", "1242864606")

# Modo de Despliegue: 'webhook' (Producción en Render) o 'polling' (Local)
RUN_MODE = os.getenv("RUN_MODE", "webhook" if os.getenv("RENDER") or os.getenv("PORT") else "polling").lower()
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://nexus-reseller-hub.onrender.com/webhook")

# Base de Datos JSON Local
DATA_DB_PATH = os.path.join(BASE_DIR, "bot_db.json")

def load_db() -> Dict[str, Any]:
    if os.path.exists(DATA_DB_PATH):
        try:
            with open(DATA_DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando DB local: {e}")
    return {"balances": {}, "orders": {}, "users": {}}

def save_db(data: Dict[str, Any]):
    try:
        with open(DATA_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error guardando DB local: {e}")

DB = load_db()

def get_user_balance(user_id: int) -> float:
    return float(DB.get("balances", {}).get(str(user_id), 0.0))

def set_user_balance(user_id: int, amount: float):
    if "balances" not in DB:
        DB["balances"] = {}
    DB["balances"][str(user_id)] = round(amount, 2)
    save_db(DB)

def track_user(user_id: int, username: str, first_name: str):
    if "users" not in DB:
        DB["users"] = {}
    DB["users"][str(user_id)] = {
        "username": username or "",
        "first_name": first_name or "",
        "last_seen": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    save_db(DB)

def record_user_order(user_id: int, order_data: dict):
    u_str = str(user_id)
    if "orders" not in DB:
        DB["orders"] = {}
    if u_str not in DB["orders"]:
        DB["orders"][u_str] = []
    DB["orders"][u_str].append(order_data)
    save_db(DB)

# ============================================================================
# MOTOR DE CATÁLOGO DINÁMICO (BUNNY API)
# ============================================================================

CACHE_PRODUCTS: List[Dict[str, Any]] = []
CACHE_TIMESTAMP: float = 0.0
CACHE_TTL_SECONDS: float = 45.0

def calculate_retail_price(cost: float) -> float:
    """Calcula margen inteligente según el costo mayorista."""
    if cost <= 0.10:
        return round(cost + 0.50, 2)
    elif cost <= 0.50:
        return round(cost + 1.20, 2)
    elif cost <= 1.00:
        return round(cost + 2.00, 2)
    elif cost <= 3.00:
        return round(cost + 2.50, 2)
    elif cost <= 6.00:
        return round(cost + 3.20, 2)
    else:
        return round(cost + 4.00, 2)

async def fetch_live_products(force_refresh: bool = False) -> List[Dict[str, Any]]:
    global CACHE_PRODUCTS, CACHE_TIMESTAMP
    now = time.time()
    if not force_refresh and CACHE_PRODUCTS and (now - CACHE_TIMESTAMP < CACHE_TTL_SECONDS):
        return CACHE_PRODUCTS

    headers = {
        "Authorization": f"Bearer {BUNNY_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{BUNNY_API_URL}/products", headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                raw_products = data.get("products", [])
                
                processed = []
                for p in raw_products:
                    cost = float(p.get("price_usdt") or p.get("your_cost") or 1.0)
                    retail = calculate_retail_price(cost)
                    
                    desc = p.get("description", "")
                    import re
                    desc_clean = re.sub(r'\[emoji:\d+\]', '•', desc)

                    processed.append({
                        "id": int(p.get("id")),
                        "name": p.get("name", "Producto"),
                        "description": desc_clean,
                        "cost": cost,
                        "retail_price": retail,
                        "stock": p.get("stock", 0),
                        "duration": p.get("duration", "N/A"),
                        "type": p.get("type", "tools"),
                        "requires_email": p.get("requires_email", False)
                    })

                CACHE_PRODUCTS = processed
                CACHE_TIMESTAMP = now
                return processed
    except Exception as e:
        logger.error(f"Error conectando con Bunny API: {e}")

    return CACHE_PRODUCTS

def categorize_product(prod: Dict[str, Any]) -> str:
    name = prod["name"].lower()
    desc = prod["description"].lower()
    full_text = f"{name} {desc}"

    if any(k in full_text for k in ["gemini", "leonardo", "veo", "claude", "chatgpt", "gpt", "perplexity", "lovable", "ai"]):
        return "cat_ai"
    elif any(k in full_text for k in ["canva", "capcut", "figma", "adobe", "creative", "design", "video"]):
        return "cat_design"
    elif any(k in full_text for k in ["replit", "office", "outlook", "mail", "code", "jetbrains", "copilot", "notion", "cursor"]):
        return "cat_dev"
    elif any(k in full_text for k in ["vpn", "surfshark", "nord", "proxy", "security"]):
        return "cat_vpn"
    else:
        return "cat_other"

# ============================================================================
# TECLADOS TELEGRAM INTERACTIVOS
# ============================================================================

def get_main_menu_keyboard():
    buttons = [
        [InlineKeyboardButton("🤖 Modelos de IA & Video", callback_data="cat_ai"),
         InlineKeyboardButton("🎨 Diseño & Gráficos", callback_data="cat_design")],
        [InlineKeyboardButton("💻 Programación & Dev Tools", callback_data="cat_dev"),
         InlineKeyboardButton("🔐 VPN & Privacidad", callback_data="cat_vpn")],
        [InlineKeyboardButton("📦 Ver Todos los Productos en Vivo", callback_data="cat_all")],
        [InlineKeyboardButton("💳 Mi Saldo / Recargar", callback_data="recharge_flow"),
         InlineKeyboardButton("📦 Mis Compras", callback_data="view_my_orders")],
        [InlineKeyboardButton("💬 Soporte & Ayuda", callback_data="support_info")]
    ]
    return InlineKeyboardMarkup(buttons)

async def get_products_inline_keyboard(cat_id: str):
    products = await fetch_live_products()
    buttons = []

    for p in products:
        p_cat = categorize_product(p)
        if cat_id == "cat_all" or p_cat == cat_id:
            stock_val = str(p["stock"]).lower()
            is_in_stock = (stock_val == "unlimited") or (isinstance(p["stock"], int) and p["stock"] > 0) or (stock_val.isdigit() and int(stock_val) > 0)
            
            icon = "🟢" if is_in_stock else "🔴"
            btn_text = f"{icon} {p['name']} — ${p['retail_price']:.2f} USDT"
            buttons.append([InlineKeyboardButton(btn_text, callback_data=f"prod_{p['id']}")])

    buttons.append([InlineKeyboardButton("🔙 Volver al Menú Principal", callback_data="show_categories")])
    return InlineKeyboardMarkup(buttons)

def get_product_action_keyboard(product: Dict[str, Any]):
    stock_val = str(product["stock"]).lower()
    is_in_stock = (stock_val == "unlimited") or (isinstance(product["stock"], int) and product["stock"] > 0) or (stock_val.isdigit() and int(stock_val) > 0)
    
    keyboard = []
    if is_in_stock:
        keyboard.append([InlineKeyboardButton(f"⚡ Comprar Ahora (${product['retail_price']:.2f} USDT)", callback_data=f"buy_{product['id']}")])
    else:
        keyboard.append([InlineKeyboardButton("❌ Agotado Temporalmente", callback_data="out_of_stock")])
    
    keyboard.append([InlineKeyboardButton("🔙 Volver al Catálogo", callback_data="show_categories")])
    return InlineKeyboardMarkup(keyboard)

def get_recharge_keyboard():
    buttons = [
        [InlineKeyboardButton("🟡 USDT BEP-20 (BNB Chain)", callback_data="wallet_bep20"),
         InlineKeyboardButton("🔴 USDT TRC-20 (Tron)", callback_data="wallet_trc20")],
        [InlineKeyboardButton("🟣 Solana (SOL / USDT)", callback_data="wallet_sol"),
         InlineKeyboardButton("🟠 Bitcoin (BTC)", callback_data="wallet_btc")],
        [InlineKeyboardButton("🔵 Todas las Redes EVM", callback_data="wallet_evm")],
        [InlineKeyboardButton("🤖 Pagar con @CryptoBot", url="https://t.me/CryptoBot")],
        [InlineKeyboardButton("🔙 Volver al Menú Principal", callback_data="show_categories")]
    ]
    return InlineKeyboardMarkup(buttons)

# ============================================================================
# TELEGRAM COMMAND & CALLBACK HANDLERS
# ============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    name = user.first_name or "Cliente"
    username = user.username or ""
    track_user(user_id, username, name)
    balance = get_user_balance(user_id)
    
    welcome_text = (
        f"⚡ *¡Bienvenido a Nexus Digital Store, {name}!* ⚡\n\n"
        f"🔥 *Catálogo Oficial conectado 100% en vivo a Bunny Tools.*\n"
        f"🚀 _Entrega automatizada e instantánea en 1 segundo vía API._\n\n"
        f"👤 *Tu ID de Cliente:* `{user_id}`\n"
        f"💰 *Tu Saldo Disponible:* `${balance:.2f} USDT`\n\n"
        f"📂 *Selecciona una opción para comenzar:*"
    )
    if update.message:
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return
    
    supplier_balance = await get_supplier_balance()
    products = await fetch_live_products(force_refresh=True)
    total_users = len(DB.get("users", {}))
    total_orders = sum(len(orders) for orders in DB.get("orders", {}).values())
    total_customer_balance = sum(DB.get("balances", {}).values())
    
    msg = (
        f"👑 *PANEL DE CONTROL ADMINISTRADOR — NEXUS STORE*\n\n"
        f"👤 *Admin ID:* `{user_id}` (@Cctes001)\n"
        f"🏦 *Saldo Mayorista Bunny:* `{supplier_balance}`\n"
        f"📦 *Productos en Catálogo:* `{len(products)}`\n"
        f"👥 *Clientes Registrados:* `{total_users}`\n"
        f"📊 *Órdenes Totales Despachadas:* `{total_orders}`\n"
        f"💳 *Saldo Total en Billeteras de Clientes:* `${total_customer_balance:.2f} USDT`\n\n"
        f"👉 *Comandos de Gestión:*\n"
        f"• `/dar_saldo <USER_ID> <MONTO>` — Acredita saldo\n"
        f"• `/quitar_saldo <USER_ID> <MONTO>` — Descuenta saldo\n"
        f"• `/productos` — Ver costos mayoristas vs venta\n"
        f"• `/recarga_bunny` — Direcciones para recargar API Bunny\n"
        f"• `/catalogo` — Vista de cliente"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def recarga_bunny_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return
    
    msg = (
        f"🐰 *BILLETERAS MAYORISTAS BUNNY TOOLS (RECARGA API)*\n\n"
        f"Transfiere entre *$3 a $5 USDT* a una de estas direcciones para recargar tu saldo mayorista de despacho:\n\n"
        f"🔶 *USDT BEP-20 (BNB Smart Chain):*\n`{SUPPLIER_WALLET_BSC}`\n\n"
        f"🔴 *USDT TRC-20 (Tron):*\n`{SUPPLIER_WALLET_TRON}`\n\n"
        f"💳 *Bybit Pay UID:* `{SUPPLIER_BYBIT_UID}`\n"
        f"💳 *Binance Pay ID:* `{SUPPLIER_BINANCE_PAY_ID}`\n\n"
        f"⚠️ *Nota:* Una vez enviado, pega el TxHash o ID de transferencia en el bot de Bunny para acreditar el saldo instantáneamente."
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def productos_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return
    products = await fetch_live_products(force_refresh=True)
    msg = "📊 *TABLA MAYORISTA DE PRODUCTOS (BUNNY LIVE):*\n\n"
    for p in products:
        margin = p['retail_price'] - p['cost']
        msg += f"• *ID {p['id']}:* {p['name']}\n  Costo: `${p['cost']:.2f}` ➔ Venta: `${p['retail_price']:.2f}` | Ganancia: `+${margin:.2f}` | Stock: `{p['stock']}`\n\n"
    
    if len(msg) > 4000:
        for i in range(0, len(msg), 4000):
            await update.message.reply_text(msg[i:i+4000], parse_mode="Markdown")
    else:
        await update.message.reply_text(msg, parse_mode="Markdown")

async def dar_saldo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return
    if len(context.args) < 2:
        await update.message.reply_text("ℹ️ Uso: `/dar_saldo <USER_ID> <MONTO>`\nEjemplo: `/dar_saldo 1849945160 5.0`")
        return
    try:
        target_id = int(context.args[0])
        amount = float(context.args[1])
        new_bal = get_user_balance(target_id) + amount
        set_user_balance(target_id, new_bal)
        await update.message.reply_text(f"✅ *Saldo Acreditado:*\n👤 Usuario: `{target_id}`\n💰 Monto: `+${amount:.2f} USDT`\n💳 Nuevo Saldo: `${new_bal:.2f} USDT`", parse_mode="Markdown")
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text=f"🎉 *¡Recarga acreditada con éxito!*\n\n💰 Has recibido: `+${amount:.2f} USDT`\n💳 Saldo actual: `${new_bal:.2f} USDT`\n\n_Ya puedes realizar tus compras en el catálogo._",
                parse_mode="Markdown",
                reply_markup=get_main_menu_keyboard()
            )
        except Exception as err:
            logger.warning(f"No se pudo notificar al usuario {target_id}: {err}")
    except ValueError:
        await update.message.reply_text("❌ Error: Monto o ID inválido.")

async def quitar_saldo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return
    if len(context.args) < 2:
        await update.message.reply_text("ℹ️ Uso: `/quitar_saldo <USER_ID> <MONTO>`")
        return
    try:
        target_id = int(context.args[0])
        amount = float(context.args[1])
        new_bal = max(0.0, get_user_balance(target_id) - amount)
        set_user_balance(target_id, new_bal)
        await update.message.reply_text(f"✅ *Saldo Descontado:*\n👤 Usuario: `{target_id}`\n💰 Descuento: `-${amount:.2f} USDT`\n💳 Nuevo Saldo: `${new_bal:.2f} USDT`", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ Error: Monto o ID inválido.")

async def handle_message_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip()
    user_id = update.effective_user.id
    username = update.effective_user.username or ""
    track_user(user_id, username, update.effective_user.first_name)

    if text in ["🛍️ Catálogo", "/catalogo", "Catálogo"]:
        await update.message.reply_text("📂 *CATÁLOGO DE PRODUCTOS EN VIVO*", parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
    elif text in ["💳 Mi Saldo / Recargar", "/saldo", "Saldo"]:
        balance = get_user_balance(user_id)
        deposit_text = (
            f"💳 *BILLETERA & RECARGA DE SALDO*\n\n"
            f"👤 *ID:* `{user_id}`\n"
            f"💰 *Saldo Disponible:* `${balance:.2f} USDT`\n\n"
            f"📥 *Selecciona la red con la que deseas recargar:*"
        )
        await update.message.reply_text(deposit_text, parse_mode="Markdown", reply_markup=get_recharge_keyboard())
    elif text in ["📦 Mis Compras", "/compras", "Compras"]:
        orders = DB.get("orders", {}).get(str(user_id), [])
        if not orders:
            await update.message.reply_text("📦 *No tienes compras registradas aún.*", parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
        else:
            msg = "📦 *TUS COMPRAS Y LICENCIAS ACTIVAS:*\n\n"
            for idx, ord in enumerate(orders, 1):
                msg += f"*{idx}. {ord['product_name']}*\n🔑 Clave/Cuenta: `{ord['key']}`\n📅 Fecha: {ord.get('date', 'N/A')}\n\n"
            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
    else:
        await update.message.reply_text(
            "👋 Utiliza los botones interactivos para navegar por la tienda y adquirir licencias:",
            reply_markup=get_main_menu_keyboard()
        )

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    balance = get_user_balance(user_id)

    if data in ["show_categories", "main_menu"]:
        welcome_text = (
            f"⚡ *NEXUS DIGITAL STORE — MENÚ PRINCIPAL*\n\n"
            f"👤 *Tu ID:* `{user_id}`\n"
            f"💰 *Saldo Disponible:* `${balance:.2f} USDT`\n\n"
            f"📂 *Selecciona una categoría para explorar:*"
        )
        await query.edit_message_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
    
    elif data in ["cat_ai", "cat_design", "cat_dev", "cat_vpn", "cat_all"]:
        keyboard = await get_products_inline_keyboard(data)
        category_titles = {
            "cat_ai": "🤖 Modelos de IA & Generación de Video",
            "cat_design": "🎨 Plataformas de Diseño & Gráficos",
            "cat_dev": "💻 Herramientas de Programación & Cloud",
            "cat_vpn": "🔐 VPN, Proxies & Privacidad Digital",
            "cat_all": "📦 Todos los Productos en Tiempo Real"
        }
        title = category_titles.get(data, "🏷️ Productos Disponibles")
        await query.edit_message_text(f"*{title}*\n\n_Selecciona un producto para ver características y comprar:_", parse_mode="Markdown", reply_markup=keyboard)
    
    elif data.startswith("prod_"):
        prod_id = int(data.replace("prod_", ""))
        products = await fetch_live_products()
        product = next((p for p in products if p["id"] == prod_id), None)
        if product:
            stock_val = str(product["stock"]).lower()
            is_in_stock = (stock_val == "unlimited") or (isinstance(product["stock"], int) and product["stock"] > 0) or (stock_val.isdigit() and int(stock_val) > 0)
            stock_info = f"🟢 En Stock ({product['stock']})" if is_in_stock else "🔴 Agotado"
            
            text = (
                f"📦 *{product['name']}*\n\n"
                f"📝 *Detalles:* {product['description']}\n\n"
                f"💰 *Precio:* `${product['retail_price']:.2f} USDT`\n"
                f"⏱️ *Duración:* `{product['duration']}`\n"
                f"📊 *Estado:* `{stock_info}`\n\n"
                f"💳 *Tu Saldo:* `${balance:.2f} USDT`\n"
            )
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_product_action_keyboard(product))
    
    elif data.startswith("buy_"):
        prod_id = int(data.replace("buy_", ""))
        products = await fetch_live_products()
        product = next((p for p in products if p["id"] == prod_id), None)
        if not product:
            await query.edit_message_text("❌ Producto no encontrado.", reply_markup=get_main_menu_keyboard())
            return
        
        price = product["retail_price"]
        if balance < price:
            needed = price - balance
            kb = [
                [InlineKeyboardButton("💳 Recargar Saldo Ahora", callback_data="recharge_flow")],
                [InlineKeyboardButton("🔙 Volver al Producto", callback_data=f"prod_{prod_id}")]
            ]
            await query.edit_message_text(
                f"❌ *Saldo Insuficiente*\n\n"
                f"📦 *Producto:* {product['name']}\n"
                f"💰 *Precio:* `${price:.2f} USDT`\n"
                f"💳 *Tu Saldo:* `${balance:.2f} USDT`\n"
                f"⚠️ *Te Faltan:* `${needed:.2f} USDT`\n\n"
                f"👉 Por favor, recarga saldo para completar la orden.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(kb)
            )
            return
        
        await query.edit_message_text("⏳ *Procesando orden con Bunny Tools en 1 segundo...*", parse_mode="Markdown")
        new_balance = balance - price
        set_user_balance(user_id, new_balance)
        delivered_key = await execute_wholesale_order(product["id"])
        
        order_record = {
            "product_id": product["id"],
            "product_name": product["name"],
            "key": delivered_key,
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "price": price,
            "cost": product["cost"]
        }
        record_user_order(user_id, order_record)
        
        success_text = (
            f"🎉 *¡COMPRA COMPLETADA CON ÉXITO!* 🎉\n\n"
            f"📦 *Producto:* {product['name']}\n"
            f"💰 *Monto Debitado:* `${price:.2f} USDT`\n"
            f"💳 *Saldo Restante:* `${new_balance:.2f} USDT`\n\n"
            f"🔑 *TU CREDENCIAL / LICENCIA:*\n"
            f"```\n{delivered_key}\n```\n\n"
            f"🌟 _¡Gracias por tu compra en Nexus Digital Store!_"
        )
        kb = [
            [InlineKeyboardButton("🛍️ Seguir Comprando", callback_data="show_categories")],
            [InlineKeyboardButton("📦 Ver Mis Compras", callback_data="view_my_orders")]
        ]
        await query.edit_message_text(success_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    
    elif data == "out_of_stock":
        await query.answer("⚠️ Este producto está temporalmente agotado. El stock se renueva automáticamente.", show_alert=True)
    
    elif data == "recharge_flow":
        deposit_text = (
            f"💳 *BILLETERA & RECARGA DE SALDO*\n\n"
            f"👤 *Tu ID de Cliente:* `{user_id}`\n"
            f"💰 *Saldo Actual:* `${balance:.2f} USDT`\n\n"
            f"Selecciona la red de pago para ver la dirección de depósito:"
        )
        await query.edit_message_text(deposit_text, parse_mode="Markdown", reply_markup=get_recharge_keyboard())
    
    elif data == "wallet_bep20":
        text = (
            f"🟡 *RECARGA USDT (BNB CHAIN / BEP-20)*\n\n"
            f"Envía cualquier importe en USDT por la red BNB Smart Chain a la siguiente dirección:\n\n"
            f"`{DEPOSIT_WALLET_BSC}`\n\n"
            f"⚠️ *Importante:* Envía exclusivamente por red BEP-20 (BSC).\n"
            f"Una vez realizada la transferencia, envía el comprobante o TxHash con tu ID `{user_id}` al administrador para acreditación inmediata."
        )
        kb = [[InlineKeyboardButton("💬 Notificar Pago al Admin", url="https://t.me/Cctes001")],
              [InlineKeyboardButton("🔙 Volver a Métodos de Pago", callback_data="recharge_flow")]]
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    
    elif data == "wallet_trc20":
        text = (
            f"🔴 *RECARGA USDT (TRON / TRC-20)*\n\n"
            f"Envía cualquier importe en USDT por la red Tron a la siguiente dirección:\n\n"
            f"`{DEPOSIT_WALLET_TRON}`\n\n"
            f"⚠️ *Importante:* Envía exclusivamente por red TRC-20.\n"
            f"Una vez realizada la transferencia, envía el comprobante o TxHash con tu ID `{user_id}` al administrador para acreditación inmediata."
        )
        kb = [[InlineKeyboardButton("💬 Notificar Pago al Admin", url="https://t.me/Cctes001")],
              [InlineKeyboardButton("🔙 Volver a Métodos de Pago", callback_data="recharge_flow")]]
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    
    elif data == "wallet_sol":
        text = (
            f"🟣 *RECARGA SOLANA (SOL / USDT SPL)*\n\n"
            f"Envía fondos por la red Solana a la siguiente dirección:\n\n"
            f"`{DEPOSIT_WALLET_SOL}`\n\n"
            f"Una vez realizada la transferencia, envía el comprobante con tu ID `{user_id}` al administrador."
        )
        kb = [[InlineKeyboardButton("💬 Notificar Pago al Admin", url="https://t.me/Cctes001")],
              [InlineKeyboardButton("🔙 Volver a Métodos de Pago", callback_data="recharge_flow")]]
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    
    elif data == "wallet_btc":
        text = (
            f"🟠 *RECARGA BITCOIN (BTC NATIVO)*\n\n"
            f"Dirección Bitcoin (SegWit nativo):\n\n"
            f"`{DEPOSIT_WALLET_BTC}`\n\n"
            f"Envía el comprobante con tu ID `{user_id}` para acreditarte saldo."
        )
        kb = [[InlineKeyboardButton("💬 Notificar Pago al Admin", url="https://t.me/Cctes001")],
              [InlineKeyboardButton("🔙 Volver a Métodos de Pago", callback_data="recharge_flow")]]
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    
    elif data == "wallet_evm":
        text = (
            f"🔵 *RECARGA REDES EVM (ETH, BASE, ARBITRUM, POLYGON, LINEA, OP)*\n\n"
            f"Dirección universal para todas las redes EVM:\n\n"
            f"`{DEPOSIT_WALLET_BSC}`\n\n"
            f"Compatible con USDT/USDC/ETH en Base, Arbitrum, Polygon, Optimism, Linea y Ethereum Mainnet."
        )
        kb = [[InlineKeyboardButton("💬 Notificar Pago al Admin", url="https://t.me/Cctes001")],
              [InlineKeyboardButton("🔙 Volver a Métodos de Pago", callback_data="recharge_flow")]]
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    
    elif data == "view_my_orders":
        orders = DB.get("orders", {}).get(str(user_id), [])
        if not orders:
            await query.edit_message_text(
                "📦 *No tienes compras registradas aún.*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛍️ Ver Catálogo", callback_data="show_categories")]])
            )
        else:
            msg = "📦 *TUS LICENCIAS Y COMPRAS ACTIVAS:*\n\n"
            for idx, ord in enumerate(orders, 1):
                msg += f"*{idx}. {ord['product_name']}*\n🔑 Clave/Acceso: `{ord['key']}`\n📅 Fecha: {ord.get('date', 'N/A')}\n\n"
            kb = [[InlineKeyboardButton("🛍️ Ir al Catálogo", callback_data="show_categories")]]
            await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    
    elif data == "support_info":
        text = (
            f"💬 *CENTRO DE SOPORTE & ATENCIÓN*\n\n"
            f"Si tienes alguna duda con tu compra, recarga o licencia, contáctanos directamente:\n\n"
            f"👑 *Administrador Oficial:* @Cctes001\n"
            f"🤖 *Bot de la Tienda:* @nexus_ai_store_bot\n"
            f"⚡ *Garantía:* Entrega instantánea 24/7 y reemplazo directo si surge alguna eventualidad."
        )
        kb = [[InlineKeyboardButton("💬 Contactar a @Cctes001", url="https://t.me/Cctes001")],
              [InlineKeyboardButton("🔙 Volver al Menú", callback_data="show_categories")]]
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

# ============================================================================
# FUNCIONES AUXILIARES DE BUNNY TOOLS API
# ============================================================================

async def get_supplier_balance() -> str:
    headers = {"Authorization": f"Bearer {BUNNY_API_KEY}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{BUNNY_API_URL}/balance", headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                bal = data.get("balance", data.get("wallet", "0.00"))
                return f"${bal} USDT"
    except Exception as e:
        return f"Error: {e}"
    return "$0.00 USDT"

async def execute_wholesale_order(supplier_product_id: int) -> str:
    headers = {"Authorization": f"Bearer {BUNNY_API_KEY}", "Content-Type": "application/json"}
    payload = {"product_id": int(supplier_product_id), "quantity": 1}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(f"{BUNNY_API_URL}/order", json=payload, headers=headers)
            if resp.status_code in [200, 201]:
                data = resp.json()
                delivered = data.get("delivered", [])
                if delivered and isinstance(delivered, list):
                    return str(delivered[0])
                if data.get("delivered_key"):
                    return str(data.get("delivered_key"))
                if data.get("voucher"):
                    return str(data.get("voucher"))
                return json.dumps(data, ensure_ascii=False)
            else:
                logger.error(f"Bunny order error status {resp.status_code}: {resp.text}")
    except Exception as e:
        logger.error(f"Error despachando orden con Bunny API: {e}")
    
    import uuid
    return f"NEXUS-VOUCHER-{uuid.uuid4().hex[:12].upper()} (Pendiente de sincronización)"

# ============================================================================
# LIFESPAN & FASTAPI WEB SERVER
# ============================================================================

telegram_app: Optional[Application] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global telegram_app
    logger.info("🚀 [NEXUS CORE] Inicializando motor FastAPI + Telegram Bot...")
    
    telegram_app = Application.builder().token(BOT_TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start_command))
    telegram_app.add_handler(CommandHandler("admin", admin_command))
    telegram_app.add_handler(CommandHandler("recarga_bunny", recarga_bunny_command))
    telegram_app.add_handler(CommandHandler("productos", productos_admin_command))
    telegram_app.add_handler(CommandHandler("dar_saldo", dar_saldo_command))
    telegram_app.add_handler(CommandHandler("quitar_saldo", quitar_saldo_command))
    telegram_app.add_handler(CommandHandler("catalogo", lambda u, c: handle_message_text(u, c)))
    telegram_app.add_handler(CommandHandler("saldo", lambda u, c: handle_message_text(u, c)))
    telegram_app.add_handler(CommandHandler("compras", lambda u, c: handle_message_text(u, c)))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message_text))
    telegram_app.add_handler(CallbackQueryHandler(handle_callback_query))

    await telegram_app.initialize()
    await telegram_app.start()

    if RUN_MODE == "webhook":
        logger.info(f"🌐 Configurando Telegram Webhook en: {WEBHOOK_URL}")
        try:
            webhook_success = await telegram_app.bot.set_webhook(
                url=WEBHOOK_URL,
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"]
            )
            logger.info(f"✅ Webhook establecido exitosamente: {webhook_success}")
        except Exception as e:
            logger.error(f"❌ Error estableciendo Webhook: {e}")
    else:
        logger.info("⚡ Iniciando modo Polling local...")
        await telegram_app.bot.delete_webhook(drop_pending_updates=True)
        await telegram_app.updater.start_polling(drop_pending_updates=True)
        logger.info("✅ Polling activo.")

    yield

    logger.info("🛑 Deteniendo servicios...")
    if telegram_app:
        if telegram_app.updater and telegram_app.updater.running:
            await telegram_app.updater.stop()
        await telegram_app.stop()
        await telegram_app.shutdown()
    logger.info("👋 Apagado limpio completado.")

app = FastAPI(
    title="Nexus Reseller Hub API",
    description="Motor híbrido de venta y despacho automatizado para Telegram y Web",
    version="2.0.0",
    lifespan=lifespan
)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Receptor oficial de eventos y mensajes de Telegram Webhook."""
    try:
        data = await request.json()
        if telegram_app:
            update = Update.de_json(data, telegram_app.bot)
            await telegram_app.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error procesando webhook: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Nexus Reseller Core 24/7 Enterprise",
        "bot": "@nexus_ai_store_bot",
        "mode": RUN_MODE,
        "webhook_url": WEBHOOK_URL if RUN_MODE == "webhook" else None,
        "timestamp": time.time()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "telegram_active": telegram_app is not None,
        "mode": RUN_MODE,
        "wallets_configured": {
            "bsc": bool(DEPOSIT_WALLET_BSC),
            "tron": bool(DEPOSIT_WALLET_TRON),
            "btc": bool(DEPOSIT_WALLET_BTC),
            "sol": bool(DEPOSIT_WALLET_SOL)
        }
    }

@app.get("/api/products")
async def get_products_api():
    products = await fetch_live_products()
    return {"count": len(products), "products": products}

@app.get("/api/wallets")
async def get_wallets_api():
    return {
        "deposit_wallets": {
            "bsc_bep20": DEPOSIT_WALLET_BSC,
            "tron_trc20": DEPOSIT_WALLET_TRON,
            "bitcoin": DEPOSIT_WALLET_BTC,
            "solana": DEPOSIT_WALLET_SOL,
            "evm_multichain": DEPOSIT_WALLET_BSC
        },
        "supplier_wallets": {
            "bsc": SUPPLIER_WALLET_BSC,
            "tron": SUPPLIER_WALLET_TRON,
            "bybit_uid": SUPPLIER_BYBIT_UID,
            "binance_pay_id": SUPPLIER_BINANCE_PAY_ID
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
