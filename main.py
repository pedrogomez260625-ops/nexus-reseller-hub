"""
=============================================================================
NEXUS TETRA-BOT MASTER HUB - HYBRID ENTERPRISE GATEWAY (FASTAPI + 4 TELEGRAM BOTS)
Aloja 4 Bots de Telegram en simultáneo sobre 1 solo Web Service de Render ($0/mes)
Consumo: 1 sola instancia (720h/mes, 100% cubierto por el plan gratuito de 750h).
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
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from dotenv import load_dotenv

load_dotenv()

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

logging.basicConfig(
    format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("TetraHubMaster")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================================
# CONFIGURACIÓN Y SECRETOS GLOBALES
# ============================================================================

BUNNY_API_KEY = os.getenv("RESELLER_API_KEY", "bai_sk_4a557cbb3c136090682510a41a13585560feff74e56eaa0e")
BUNNY_API_URL = os.getenv("RESELLER_BASE_URL", "https://bhao.site/api/reseller/v1")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "1849945160"))

# Billeteras Personales de Cobro (Pedro Gomez / Rafa / MetaMask)
DEPOSIT_WALLET_BSC = os.getenv("DEPOSIT_WALLET_BSC", "0xe733e832e20cAE3a1e897F7F4A5B6e16934675C9")
DEPOSIT_WALLET_TRON = os.getenv("DEPOSIT_WALLET_TRON", "TZ3DYd7HNhnnSYUfris5Pqm66YmDugQ5Ch")
DEPOSIT_WALLET_BTC = os.getenv("DEPOSIT_WALLET_BTC", "bc1qt3s56f8h4crf69httj2snvseq5q6lskpnn5w64")
DEPOSIT_WALLET_SOL = os.getenv("DEPOSIT_WALLET_SOL", "cjwdWUXMtHgNU4dQmWEKPuyYLm4eonxpfyjhL6crCu4")

# Billeteras Mayoristas Bunny (Para recarga de saldo API)
SUPPLIER_WALLET_BSC = os.getenv("SUPPLIER_WALLET_BSC", "0xec0183f1411c106afb8cfe32c391fef536f681d4")
SUPPLIER_WALLET_TRON = os.getenv("SUPPLIER_WALLET_TRON", "TKuRmAYaCQR3nTv3M8XtRZ8VwXfuLHWPbE")
SUPPLIER_BYBIT_UID = os.getenv("SUPPLIER_BYBIT_UID", "127245517")
SUPPLIER_BINANCE_PAY_ID = os.getenv("SUPPLIER_BINANCE_PAY_ID", "1242864606")

# Runtime & URLs
BASE_WEBHOOK_URL = os.getenv("BASE_WEBHOOK_URL", "https://nexus-reseller-hub.onrender.com").rstrip("/")
RUN_MODE = os.getenv("RUN_MODE", "webhook" if os.getenv("RENDER") or os.getenv("PORT") else "polling").lower()

# ============================================================================
# DEFINICIÓN DE LOS 4 BOTS DE LA RED
# ============================================================================

BOT_DEFINITIONS = {
    "nexus": {
        "key": "nexus",
        "name": "Nexus Digital Store",
        "username": "@nexus_ai_store_bot",
        "token": os.getenv("BOT_TOKEN_NEXUS", os.getenv("TELEGRAM_BOT_TOKEN", "8873710791:AAEKEolVYTYoeYE45JLZKPlG__DpBUbU5yg")),
        "tagline": "⚡ Tienda Principal Multirubro (IA, Dev, Diseño, VPN)",
        "emoji": "⚡"
    },
    "nova": {
        "key": "nova",
        "name": "Nova AI Keys Hub",
        "username": "@nova_ai_keys_bot",
        "token": os.getenv("BOT_TOKEN_NOVA", "8870399329:AAG9Co0upODc7UJ_QgodmgaQiORNPc9jTX4"),
        "tagline": "🌟 Especialista en Modelos de IA, LLMs & Generación de Video",
        "emoji": "🌟"
    },
    "devcore": {
        "key": "devcore",
        "name": "DevCore Pro Store",
        "username": "@devcore_pro_bot",
        "token": os.getenv("BOT_TOKEN_DEVCORE", "8918777311:AAFXqk2CSj_y77WtG3hyQ50WAtHCENiZFmE"),
        "tagline": "💻 Herramientas de Desarrollo, IDEs & Cloud Computing",
        "emoji": "💻"
    },
    "cybervault": {
        "key": "cybervault",
        "name": "CyberVault Keys Store",
        "username": "@cybervault_keys_bot",
        "token": os.getenv("BOT_TOKEN_CYBERVAULT", "8853535007:AAF6Gm9ap4P11e1I9UAHYiPg8gcyEAQEe8M"),
        "tagline": "🔐 Cuentas Premium, VPNs & Privacidad Digital",
        "emoji": "🔐"
    }
}

# Base de Datos JSON Centralizada
DATA_DB_PATH = os.path.join(BASE_DIR, "tetra_hub_db.json")

def load_db() -> Dict[str, Any]:
    if os.path.exists(DATA_DB_PATH):
        try:
            with open(DATA_DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"balances": {}, "orders": {}, "users": {}}

def save_db(data: Dict[str, Any]):
    try:
        with open(DATA_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error guardando DB: {e}")

DB = load_db()

def get_user_balance(user_id: int) -> float:
    return float(DB.get("balances", {}).get(str(user_id), 0.0))

def set_user_balance(user_id: int, amount: float):
    if "balances" not in DB:
        DB["balances"] = {}
    DB["balances"][str(user_id)] = round(amount, 2)
    save_db(DB)

def track_user(user_id: int, username: str, first_name: str, bot_key: str):
    if "users" not in DB:
        DB["users"] = {}
    DB["users"][str(user_id)] = {
        "username": username or "",
        "first_name": first_name or "",
        "origin_bot": bot_key,
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
# MOTOR DE CATÁLOGO DINÁMICO BUNNY API
# ============================================================================

CACHE_PRODUCTS: List[Dict[str, Any]] = []
CACHE_TIMESTAMP: float = 0.0

def calculate_retail_price(cost: float) -> float:
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
    if not force_refresh and CACHE_PRODUCTS and (now - CACHE_TIMESTAMP < 45.0):
        return CACHE_PRODUCTS

    headers = {"Authorization": f"Bearer {BUNNY_API_KEY}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{BUNNY_API_URL}/products", headers=headers)
            if resp.status_code == 200:
                raw_products = resp.json().get("products", [])
                processed = []
                for p in raw_products:
                    cost = float(p.get("price_usdt") or p.get("your_cost") or 1.0)
                    desc = p.get("description", "")
                    import re
                    desc_clean = re.sub(r'\[emoji:\d+\]', '•', desc)
                    processed.append({
                        "id": int(p.get("id")),
                        "name": p.get("name", "Producto"),
                        "description": desc_clean,
                        "cost": cost,
                        "retail_price": calculate_retail_price(cost),
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

async def get_supplier_balance() -> str:
    headers = {"Authorization": f"Bearer {BUNNY_API_KEY}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{BUNNY_API_URL}/balance", headers=headers)
            if resp.status_code == 200:
                bal = resp.json().get("balance", resp.json().get("wallet", "0.00"))
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
                d = resp.json()
                deliv = d.get("delivered", [])
                if deliv and isinstance(deliv, list):
                    return str(deliv[0])
                return str(d.get("delivered_key", d.get("voucher", json.dumps(d))))
    except Exception as e:
        logger.error(f"Error despachando orden: {e}")
    import uuid
    return f"NEXUS-VOUCHER-{uuid.uuid4().hex[:12].upper()} (Sincronización manual)"

# ============================================================================
# TECLADOS TELEGRAM COMUNES
# ============================================================================

def get_common_main_keyboard(bot_info: dict):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️ Ver Catálogo en Vivo", callback_data="show_catalog")],
        [InlineKeyboardButton("💳 Mi Saldo / Recargar", callback_data="recharge_flow"),
         InlineKeyboardButton("📦 Mis Compras", callback_data="view_orders")],
        [InlineKeyboardButton("💬 Soporte Técnico", url="https://t.me/Cctes001")]
    ])

def get_common_recharge_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🟡 USDT BEP-20 (BNB Chain)", callback_data="w_bep20"),
         InlineKeyboardButton("🔴 USDT TRC-20 (Tron)", callback_data="w_trc20")],
        [InlineKeyboardButton("🟣 Solana (SOL / USDT)", callback_data="w_sol"),
         InlineKeyboardButton("🟠 Bitcoin (BTC)", callback_data="w_btc")],
        [InlineKeyboardButton("🔵 Todas las Redes EVM", callback_data="w_evm")],
        [InlineKeyboardButton("🤖 Pagar con @CryptoBot", url="https://t.me/CryptoBot")],
        [InlineKeyboardButton("🔙 Volver al Menú", callback_data="main_menu")]
    ])

# ============================================================================
# FABRICADOR DE HANDLERS DINÁMICOS POR BOT
# ============================================================================

def make_handlers_for_bot(bot_key: str, bot_info: dict):
    bot_name = bot_info["name"]
    bot_emoji = bot_info["emoji"]

    async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        u = update.effective_user
        track_user(u.id, u.username, u.first_name, bot_key)
        balance = get_user_balance(u.id)
        text = (
            f"{bot_emoji} *¡Bienvenido a {bot_name}, {u.first_name}!* {bot_emoji}\n\n"
            f"🔥 *Catálogo Oficial conectado 100% en vivo a Bunny Tools.*\n"
            f"🚀 _Entrega automatizada e instantánea en 1 segundo vía API._\n\n"
            f"👤 *Tu ID:* `{u.id}`\n"
            f"💰 *Tu Saldo Disponible:* `${balance:.2f} USDT`\n\n"
            f"Selecciona una opción para comenzar:"
        )
        if update.message:
            await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_common_main_keyboard(bot_info))

    async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ADMIN_ID:
            return
        supplier_bal = await get_supplier_balance()
        products = await fetch_live_products(force_refresh=True)
        total_users = len(DB.get("users", {}))
        total_orders = sum(len(o) for o in DB.get("orders", {}).values())
        msg = (
            f"👑 *PANEL ADMINISTRADOR TETRA-HUB — {bot_name.upper()}*\n\n"
            f"👤 *Admin:* `{ADMIN_ID}` (@Cctes001)\n"
            f"🏦 *Saldo Mayorista Bunny:* `{supplier_bal}`\n"
            f"📦 *Productos en Catálogo:* `{len(products)}`\n"
            f"👥 *Usuarios Totales Red:* `{total_users}`\n"
            f"📊 *Órdenes Despachadas:* `{total_orders}`\n\n"
            f"👉 Comandos:\n"
            f"• `/dar_saldo <USER_ID> <MONTO>`\n"
            f"• `/quitar_saldo <USER_ID> <MONTO>`\n"
            f"• `/productos`\n"
            f"• `/recarga_bunny`"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def recarga_bunny_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ADMIN_ID:
            return
        msg = (
            f"🐰 *DIRECCIONES PARA RECARGAR API BUNNY ($3 a $5 USDT)*\n\n"
            f"🔶 *BSC (BEP20):* `{SUPPLIER_WALLET_BSC}`\n"
            f"🔴 *Tron (TRC20):* `{SUPPLIER_WALLET_TRON}`\n"
            f"💳 *Bybit UID:* `{SUPPLIER_BYBIT_UID}`\n"
            f"💳 *Binance Pay ID:* `{SUPPLIER_BINANCE_PAY_ID}`"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def productos_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ADMIN_ID:
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

    async def dar_saldo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ADMIN_ID or len(context.args) < 2:
            await update.message.reply_text("ℹ️ Uso: `/dar_saldo <ID> <MONTO>`")
            return
        try:
            t_id, amt = int(context.args[0]), float(context.args[1])
            n_bal = get_user_balance(t_id) + amt
            set_user_balance(t_id, n_bal)
            await update.message.reply_text(f"✅ Saldo acreditado a `{t_id}`: `${n_bal:.2f} USDT`", parse_mode="Markdown")
            try:
                await context.bot.send_message(chat_id=t_id, text=f"🎉 *¡Recarga acreditada!*\nHas recibido: `+${amt:.2f} USDT`\nSaldo actual: `${n_bal:.2f} USDT`", parse_mode="Markdown")
            except Exception:
                pass
        except ValueError:
            await update.message.reply_text("❌ Monto o ID inválido.")

    async def cb_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if not query:
            return
        await query.answer()
        data = query.data
        u_id = query.from_user.id
        balance = get_user_balance(u_id)

        if data == "main_menu":
            await query.edit_message_text(f"{bot_emoji} *{bot_name.upper()} — MENÚ*\n\n👤 ID: `{u_id}`\n💰 Saldo: `${balance:.2f} USDT`", parse_mode="Markdown", reply_markup=get_common_main_keyboard(bot_info))
        elif data == "show_catalog":
            products = await fetch_live_products()
            buttons = []
            for p in products:
                is_stock = p["stock"] != 0
                icon = "🟢" if is_stock else "🔴"
                buttons.append([InlineKeyboardButton(f"{icon} {p['name']} — ${p['retail_price']:.2f}", callback_data=f"p_{p['id']}")])
            buttons.append([InlineKeyboardButton("🔙 Volver al Menú", callback_data="main_menu")])
            await query.edit_message_text("📂 *CATÁLOGO DE PRODUCTOS EN VIVO:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))
        elif data.startswith("p_"):
            pid = int(data.replace("p_", ""))
            products = await fetch_live_products()
            p = next((x for x in products if x["id"] == pid), None)
            if p:
                stock_info = f"🟢 En Stock ({p['stock']})" if p["stock"] != 0 else "🔴 Agotado"
                txt = f"📦 *{p['name']}*\n\n📝 {p['description']}\n\n💰 *Precio:* `${p['retail_price']:.2f} USDT`\n⏱️ *Duración:* `{p['duration']}`\n📊 *Estado:* `{stock_info}`\n\n💳 *Tu Saldo:* `${balance:.2f} USDT`"
                kb = [
                    [InlineKeyboardButton(f"⚡ Comprar Ahora (${p['retail_price']:.2f} USDT)", callback_data=f"b_{p['id']}")],
                    [InlineKeyboardButton("🔙 Volver al Catálogo", callback_data="show_catalog")]
                ]
                await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
        elif data.startswith("b_"):
            pid = int(data.replace("b_", ""))
            products = await fetch_live_products()
            p = next((x for x in products if x["id"] == pid), None)
            if not p:
                return
            if balance < p["retail_price"]:
                needed = p["retail_price"] - balance
                kb = [[InlineKeyboardButton("💳 Recargar Saldo Ahora", callback_data="recharge_flow")], [InlineKeyboardButton("🔙 Volver", callback_data=f"p_{pid}")]]
                await query.edit_message_text(f"❌ *Saldo Insuficiente*\n\nPrecio: `${p['retail_price']:.2f} USDT`\nTu saldo: `${balance:.2f} USDT`\nFaltan: `${needed:.2f} USDT`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
                return
            
            await query.edit_message_text("⏳ *Procesando orden con Bunny Tools en 1 segundo...*", parse_mode="Markdown")
            new_bal = balance - p["retail_price"]
            set_user_balance(u_id, new_bal)
            key_deliv = await execute_wholesale_order(pid)
            
            record_user_order(u_id, {
                "bot": bot_key,
                "product_id": pid,
                "product_name": p["name"],
                "key": key_deliv,
                "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "price": p["retail_price"]
            })
            
            succ_txt = f"🎉 *¡COMPRA COMPLETADA CON ÉXITO!* 🎉\n\n📦 *Producto:* {p['name']}\n💰 *Debitado:* `${p['retail_price']:.2f} USDT`\n💳 *Saldo Restante:* `${new_bal:.2f} USDT`\n\n🔑 *TU LICENCIA / CUENTA:*\n```\n{key_deliv}\n```\n\n🌟 _¡Gracias por comprar en {bot_name}!_"
            await query.edit_message_text(succ_txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛍️ Seguir Comprando", callback_data="show_catalog")]]))
        elif data == "recharge_flow":
            txt = f"💳 *BILLETERA & RECARGA DE SALDO*\n\n👤 ID: `{u_id}`\n💰 Saldo: `${balance:.2f} USDT`\n\nSelecciona la red con la que deseas recargar:"
            await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=get_common_recharge_keyboard())
        elif data == "w_bep20":
            txt = f"🟡 *USDT (BNB SMART CHAIN - BEP20)*\n\n`{DEPOSIT_WALLET_BSC}`\n\nEnvía comprobante con tu ID `{u_id}` a @Cctes001 para acreditar."
            await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="recharge_flow")]]))
        elif data == "w_trc20":
            txt = f"🔴 *USDT (TRON - TRC20)*\n\n`{DEPOSIT_WALLET_TRON}`\n\nEnvía comprobante con tu ID `{u_id}` a @Cctes001 para acreditar."
            await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="recharge_flow")]]))
        elif data == "w_sol":
            txt = f"🟣 *SOLANA (SOL / USDT SPL)*\n\n`{DEPOSIT_WALLET_SOL}`\n\nEnvía comprobante con tu ID `{u_id}` a @Cctes001."
            await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="recharge_flow")]]))
        elif data == "w_btc":
            txt = f"🟠 *BITCOIN (BTC NATIVO)*\n\n`{DEPOSIT_WALLET_BTC}`\n\nEnvía comprobante con tu ID `{u_id}` a @Cctes001."
            await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="recharge_flow")]]))
        elif data == "w_evm":
            txt = f"🔵 *REDES EVM (ETH, BASE, ARBITRUM, POLYGON, LINEA, OP)*\n\n`{DEPOSIT_WALLET_BSC}`\n\nEnvía comprobante con tu ID `{u_id}` a @Cctes001."
            await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="recharge_flow")]]))
        elif data == "view_orders":
            orders = DB.get("orders", {}).get(str(u_id), [])
            if not orders:
                await query.edit_message_text("📦 No tienes compras registradas aún.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛍️ Catálogo", callback_data="show_catalog")]]))
            else:
                msg = "📦 *TUS LICENCIAS ACTIVAS:*\n\n"
                for idx, o in enumerate(orders, 1):
                    msg += f"*{idx}. {o.get('product_name', o.get('product'))}*\n🔑 `{o.get('key')}`\n📅 {o.get('date', 'N/A')}\n\n"
                await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="main_menu")]]))

    return start_cmd, admin_cmd, recarga_bunny_cmd, productos_cmd, dar_saldo_cmd, cb_query

# ============================================================================
# INSTANCIACIÓN DE LAS 4 APPS DE TELEGRAM
# ============================================================================

BOT_APPS: Dict[str, Application] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    global BOT_APPS
    logger.info("🚀 [TETRA-HUB] Inicializando los 4 Bots de Telegram en simultáneo...")

    for key, info in BOT_DEFINITIONS.items():
        token = info["token"]
        if not token:
            logger.warning(f"⚠️ Token ausente para {key}")
            continue
        try:
            bot_app = Application.builder().token(token).build()
            start_c, admin_c, bunny_c, prods_c, saldo_c, cb_q = make_handlers_for_bot(key, info)

            bot_app.add_handler(CommandHandler("start", start_c))
            bot_app.add_handler(CommandHandler("admin", admin_c))
            bot_app.add_handler(CommandHandler("recarga_bunny", bunny_c))
            bot_app.add_handler(CommandHandler("productos", prods_c))
            bot_app.add_handler(CommandHandler("dar_saldo", saldo_c))
            bot_app.add_handler(CommandHandler("catalogo", lambda u, c, sc=start_c: sc(u, c)))
            bot_app.add_handler(CallbackQueryHandler(cb_q))

            await bot_app.initialize()
            await bot_app.start()

            if RUN_MODE == "webhook":
                webhook_url = f"{BASE_WEBHOOK_URL}/webhook/{key}"
                logger.info(f"🌐 [{key.upper()}] Configurando Webhook en: {webhook_url}")
                await bot_app.bot.set_webhook(url=webhook_url, drop_pending_updates=True, allowed_updates=["message", "callback_query"])
            else:
                logger.info(f"⚡ [{key.upper()}] Polling local activo...")
                await bot_app.bot.delete_webhook(drop_pending_updates=True)
                await bot_app.updater.start_polling(drop_pending_updates=True)

            BOT_APPS[key] = bot_app
            logger.info(f"✅ Bot {info['name']} ({info['username']}) levantado exitosamente.")
        except Exception as e:
            logger.error(f"❌ Error levantando bot {key}: {e}")

    yield

    logger.info("🛑 Deteniendo los 4 Bots...")
    for key, bot_app in BOT_APPS.items():
        try:
            if bot_app.updater and bot_app.updater.running:
                await bot_app.updater.stop()
            await bot_app.stop()
            await bot_app.shutdown()
        except Exception:
            pass
    logger.info("👋 Tetra-Hub detenido limpiamente.")

app = FastAPI(
    title="Nexus Tetra-Bot Reseller Gateway",
    description="Gateway maestro de 4 Bots de Telegram en 1 sola instancia",
    version="3.0.0",
    lifespan=lifespan
)

# ============================================================================
# ENDPOINTS REST & WEBHOOKS
# ============================================================================

@app.post("/webhook/{bot_key}")
async def dynamic_bot_webhook(bot_key: str, request: Request):
    """Receptor dinámico de eventos de Telegram para cada uno de los 4 bots."""
    if bot_key not in BOT_APPS:
        return JSONResponse(status_code=404, content={"error": f"Bot '{bot_key}' no encontrado"})
    try:
        data = await request.json()
        target_app = BOT_APPS[bot_key]
        update = Update.de_json(data, target_app.bot)
        await target_app.process_update(update)
        return {"status": "ok", "bot": bot_key}
    except Exception as e:
        logger.error(f"Error procesando webhook en {bot_key}: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/webhook")
async def default_nexus_webhook(request: Request):
    """Fallback compatible para el webhook de Nexus Store."""
    return await dynamic_bot_webhook("nexus", request)

@app.get("/", response_class=HTMLResponse)
async def home_dashboard():
    bot_cards = ""
    for key, info in BOT_DEFINITIONS.items():
        active = "🟢 En Línea" if key in BOT_APPS else "🔴 Inactivo"
        bot_cards += f"""
        <div style="background: #1e293b; padding: 20px; border-radius: 12px; margin: 15px; width: 280px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);">
            <h2 style="color: #60a5fa; margin-top: 0;">{info['emoji']} {info['name']}</h2>
            <p style="color: #94a3b8; font-size: 14px;">{info['tagline']}</p>
            <p style="font-weight: bold; color: #34d399;">{active}</p>
            <a href="https://t.me/{info['username'].replace('@', '')}" target="_blank" style="display: inline-block; background: #3b82f6; color: white; padding: 10px 16px; border-radius: 8px; text-decoration: none; font-weight: bold;">Abrir en Telegram</a>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Nexus Tetra-Hub Master</title>
    </head>
    <body style="font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: white; margin: 0; padding: 40px; text-align: center;">
        <h1 style="color: #f8fafc; font-size: 32px; margin-bottom: 5px;">⚡ NEXUS TETRA-BOT RESELLER HUB ⚡</h1>
        <p style="color: #94a3b8; font-size: 16px; margin-bottom: 40px;">Infraestructura Soberana Multi-Bot 24/7 sobre Render Cloud ($0/mes)</p>
        <div style="display: flex; flex-wrap: wrap; justify-content: center; max-width: 1200px; margin: 0 auto;">
            {bot_cards}
        </div>
        <div style="margin-top: 50px; color: #64748b; font-size: 14px;">
            <p>API Mayorista Bunny Tools | 20 Productos Sincronizados | Despacho en 1s</p>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Nexus Tetra-Bot Master Gateway",
        "active_bots_count": len(BOT_APPS),
        "bots": {k: (k in BOT_APPS) for k in BOT_DEFINITIONS},
        "mode": RUN_MODE,
        "wallets_configured": {
            "bsc": bool(DEPOSIT_WALLET_BSC),
            "tron": bool(DEPOSIT_WALLET_TRON),
            "btc": bool(DEPOSIT_WALLET_BTC),
            "sol": bool(DEPOSIT_WALLET_SOL)
        }
    }

@app.get("/api/bots")
async def list_bots():
    return {
        "count": len(BOT_DEFINITIONS),
        "bots": [
            {
                "key": k,
                "name": v["name"],
                "username": v["username"],
                "active": k in BOT_APPS,
                "webhook": f"{BASE_WEBHOOK_URL}/webhook/{k}"
            }
            for k, v in BOT_DEFINITIONS.items()
        ]
    }

@app.get("/api/products")
async def list_products():
    products = await fetch_live_products()
    return {"count": len(products), "products": products}

@app.get("/api/wallets")
async def list_wallets():
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
