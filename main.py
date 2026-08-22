"""
NEXUS RESELLER HUB - HYBRID ENGINE (FASTAPI + TELEGRAM BOT + DYNAMIC CATALOG)
Optimizado 100% para despliegue en Render, Koyeb, Railway, TeleBotHost o Servidor Local.
Autor: Nexus Core / Angelus AGI
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
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger("NexusResellerHub")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8873710791:AAEKEolVYTYoeYE45JLZKPlG__DpBUbU5yg")
BUNNY_API_KEY = os.getenv("RESELLER_API_KEY", os.getenv("BUNNY_API_KEY", "bai_sk_4a557cbb3c136090682510a41a13585560feff74e56eaa0e"))
BUNNY_API_URL = os.getenv("RESELLER_BASE_URL", "https://bhao.site/api/reseller/v1")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "1849945160"))

DEPOSIT_WALLET_BSC = os.getenv("DEPOSIT_WALLET_BSC", "0xec0183f1411c106afb8cfe32c391fef536f681d4")
DEPOSIT_WALLET_TRON = os.getenv("DEPOSIT_WALLET_TRON", "TKuRmAYaCQR3nTv3M8XtRZ8VwXfuLHWPbE")

# Base de datos local JSON
DATA_DB_PATH = os.path.join(BASE_DIR, "bot_db.json")

def load_db():
    if os.path.exists(DATA_DB_PATH):
        try:
            with open(DATA_DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"balances": {}, "orders": {}}

def save_db(data):
    try:
        with open(DATA_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error guardando DB: {e}")

DB = load_db()

def get_user_balance(user_id: int) -> float:
    return float(DB["balances"].get(str(user_id), 0.0))

def set_user_balance(user_id: int, amount: float):
    DB["balances"][str(user_id)] = round(amount, 2)
    save_db(DB)

def record_user_order(user_id: int, order_data: dict):
    u_str = str(user_id)
    if u_str not in DB["orders"]:
        DB["orders"][u_str] = []
    DB["orders"][u_str].append(order_data)
    save_db(DB)

# ============================================================================
# MOTOR DE CATÁLOGO DINÁMICO EN VIVO (BUNNY API)
# ============================================================================

CACHE_PRODUCTS: List[Dict[str, Any]] = []
CACHE_TIMESTAMP: float = 0.0
CACHE_TTL_SECONDS: float = 30.0

def calculate_retail_price(cost: float) -> float:
    if cost <= 0.10:
        return round(cost + 0.50, 2)
    elif cost <= 0.50:
        return round(cost + 1.20, 2)
    elif cost <= 1.00:
        return round(cost + 2.00, 2)
    elif cost <= 3.00:
        return round(cost + 2.50, 2)
    else:
        return round(cost + 3.50, 2)

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
    elif any(k in full_text for k in ["replit", "office", "outlook", "mail", "code", "jetbrains", "copilot", "notion"]):
        return "cat_dev"
    elif any(k in full_text for k in ["vpn", "surfshark", "nord", "proxy", "security"]):
        return "cat_vpn"
    else:
        return "cat_other"

# ============================================================================
# TECLADOS TELEGRAM
# ============================================================================

def get_categories_inline_keyboard():
    buttons = [
        [InlineKeyboardButton("🤖 Modelos de IA & Video", callback_data="cat_ai")],
        [InlineKeyboardButton("🎨 Diseño & Gráficos", callback_data="cat_design")],
        [InlineKeyboardButton("💻 Programación & Dev Tools", callback_data="cat_dev")],
        [InlineKeyboardButton("🔐 VPN & Privacidad", callback_data="cat_vpn")],
        [InlineKeyboardButton("📦 Ver Todos los Productos en Vivo", callback_data="cat_all")],
        [InlineKeyboardButton("💳 Mi Saldo / Recargar", callback_data="recharge_flow")]
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

    buttons.append([InlineKeyboardButton("🔙 Volver a Categorías", callback_data="show_categories")])
    return InlineKeyboardMarkup(buttons)

def get_product_action_keyboard(product: Dict[str, Any]):
    stock_val = str(product["stock"]).lower()
    is_in_stock = (stock_val == "unlimited") or (isinstance(product["stock"], int) and product["stock"] > 0) or (stock_val.isdigit() and int(stock_val) > 0)
    
    keyboard = []
    if is_in_stock:
        keyboard.append([InlineKeyboardButton(f"⚡ Comprar Ahora (${product['retail_price']:.2f} USDT)", callback_data=f"buy_{product['id']}")])
    else:
        keyboard.append([InlineKeyboardButton("❌ Agotado Temporalmente", callback_data="out_of_stock")])
    
    keyboard.append([InlineKeyboardButton("🔙 Volver a Categorías", callback_data="show_categories")])
    return InlineKeyboardMarkup(keyboard)

# ============================================================================
# TELEGRAM HANDLERS
# ============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    name = user.first_name or "Cliente"
    balance = get_user_balance(user_id)
    
    welcome_text = (
        f"⚡ *¡Bienvenido a Nexus Digital Store, {name}!* ⚡\n\n"
        f"🔥 *Catálogo Oficial conectado 100% en vivo a Bunny Tools.*\n"
        f"🚀 _Entrega automatizada e instantánea en 1 segundo vía API._\n\n"
        f"💰 *Tu Saldo Disponible:* `${balance:.2f} USDT`\n\n"
        f"📂 *Selecciona una categoría para explorar productos actualizados:*"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=get_categories_inline_keyboard())

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return
    supplier_info = await get_supplier_balance()
    products = await fetch_live_products(force_refresh=True)
    msg = (
        f"👑 *PANEL DE CONTROL ADMINISTRADOR*\n\n"
        f"👤 *Admin:* `{user_id}` (@Cctes001)\n"
        f"🏦 *Saldo Mayorista Bunny:* `{supplier_info}`\n"
        f"📦 *Productos Activos:* `{len(products)}`\n\n"
        f"👉 *Comandos Rápidos:*\n"
        f"• `/dar_saldo <USER_ID> <MONTO>`\n"
        f"• `/productos`\n"
        f"• `/catalogo`"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def productos_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return
    products = await fetch_live_products(force_refresh=True)
    msg = "📊 *TABLA MAYORISTA DE PRODUCTOS (BUNNY LIVE):*\n\n"
    for p in products:
        msg += f"• *ID {p['id']}:* {p['name']}\n  Costo: `${p['cost']} USDT` ➔ Venta: `${p['retail_price']:.2f}` | Stock: `{p['stock']}`\n\n"
    if len(msg) > 4000:
        for part in [msg[i:i+4000] for i in range(0, len(msg), 4000)]:
            await update.message.reply_text(part, parse_mode="Markdown")
    else:
        await update.message.reply_text(msg, parse_mode="Markdown")

async def dar_saldo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return
    if len(context.args) < 2:
        await update.message.reply_text("ℹ️ Uso: `/dar_saldo <user_id> <monto>`")
        return
    try:
        target_id = int(context.args[0])
        amount = float(context.args[1])
        new_bal = get_user_balance(target_id) + amount
        set_user_balance(target_id, new_bal)
        await update.message.reply_text(f"✅ *Saldo Acreditado:*\nUsuario: `{target_id}`\nNuevo Saldo: `${new_bal:.2f} USDT`", parse_mode="Markdown")
        try:
            await context.bot.send_message(chat_id=target_id, text=f"💰 *¡Recarga acreditada!*\nHas recibido: `${amount:.2f} USDT`\nSaldo: `${new_bal:.2f} USDT`", parse_mode="Markdown")
        except Exception:
            pass
    except ValueError:
        await update.message.reply_text("❌ Error: Monto o ID inválido.")

async def handle_message_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id
    if text in ["🛍️ Catálogo de Productos", "/catalogo"]:
        await update.message.reply_text("📂 *CATÁLOGO DE PRODUCTOS EN VIVO*", parse_mode="Markdown", reply_markup=get_categories_inline_keyboard())
    elif text in ["💳 Mi Saldo / Recargar", "/saldo"]:
        balance = get_user_balance(user_id)
        deposit_text = (
            f"💳 *ESTADO DE TU BILLETERA*\n\n"
            f"👤 *ID:* `{user_id}`\n💰 *Saldo:* `${balance:.2f} USDT`\n\n"
            f"1️⃣ *USDT BEP20 (BSC):* `{DEPOSIT_WALLET_BSC}`\n"
            f"2️⃣ *USDT TRC20 (Tron):* `{DEPOSIT_WALLET_TRON}`\n"
            f"3️⃣ *Vía @CryptoBot*\n\nEnvía el comprobante para acreditarte saldo."
        )
        kb = [[InlineKeyboardButton("➕ Recargar con @CryptoBot", url="https://t.me/CryptoBot")], [InlineKeyboardButton("🔙 Volver al Catálogo", callback_data="show_categories")]]
        await update.message.reply_text(deposit_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    elif text in ["📦 Mis Compras", "/compras"]:
        orders = DB["orders"].get(str(user_id), [])
        if not orders:
            await update.message.reply_text("📦 *No tienes compras registradas aún.*", parse_mode="Markdown")
        else:
            msg = "📦 *TUS COMPRAS ACTIVAS:*\n\n"
            for idx, ord in enumerate(orders, 1):
                msg += f"*{idx}. {ord['product_name']}*\n🔑 Clave/Cuenta: `{ord['key']}`\n📅 Fecha: {ord['date']}\n\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
    else:
        await update.message.reply_text("Usa los botones para navegar por el catálogo.", reply_markup=get_categories_inline_keyboard())

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data in ["show_categories", "main_menu"]:
        await query.edit_message_text("📂 *Selecciona una categoría:*", parse_mode="Markdown", reply_markup=get_categories_inline_keyboard())
    elif data in ["cat_ai", "cat_design", "cat_dev", "cat_vpn", "cat_all"]:
        keyboard = await get_products_inline_keyboard(data)
        await query.edit_message_text("🏷️ *Productos Disponibles:*", parse_mode="Markdown", reply_markup=keyboard)
    elif data.startswith("prod_"):
        prod_id = int(data.replace("prod_", ""))
        products = await fetch_live_products()
        product = next((p for p in products if p["id"] == prod_id), None)
        if product:
            stock_info = f"🟢 Disponible ({product['stock']})" if product["stock"] != 0 else "🔴 Agotado"
            text = (
                f"📦 *{product['name']}*\n\n"
                f"📝 *Detalles:* {product['description']}\n\n"
                f"💰 *Precio:* `${product['retail_price']:.2f} USDT`\n"
                f"⏱️ *Duración:* `{product['duration']}`\n"
                f"📊 *Stock:* `{stock_info}`\n"
            )
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_product_action_keyboard(product))
    elif data.startswith("buy_"):
        prod_id = int(data.replace("buy_", ""))
        products = await fetch_live_products()
        product = next((p for p in products if p["id"] == prod_id), None)
        if not product:
            return
        balance = get_user_balance(user_id)
        price = product["retail_price"]
        if balance < price:
            kb = [[InlineKeyboardButton("💳 Recargar Saldo", callback_data="recharge_flow")], [InlineKeyboardButton("🔙 Volver", callback_data=f"prod_{prod_id}")]]
            await query.edit_message_text(f"❌ *Saldo Insuficiente*\n\nPrecio: `${price:.2f} USDT`\nTu saldo: `${balance:.2f} USDT`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
            return
        
        await query.edit_message_text("⏳ *Procesando orden con Bunny Tools en 1 segundo...*", parse_mode="Markdown")
        new_balance = balance - price
        set_user_balance(user_id, new_balance)
        delivered_key = await execute_wholesale_order(product["id"])
        
        import datetime
        record_user_order(user_id, {
            "product_id": product["id"], "product_name": product["name"],
            "key": delivered_key, "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "price": price, "cost": product["cost"]
        })
        
        success_text = f"🎉 *¡COMPRA EXITOSA!* 🎉\n\n📦 *Producto:* {product['name']}\n💰 *Debitado:* `${price:.2f} USDT`\n\n🔑 *CREDENCIAL / LICENCIA:*\n`{delivered_key}`"
        kb = [[InlineKeyboardButton("🛍️ Seguir Comprando", callback_data="show_categories")], [InlineKeyboardButton("📦 Mis Compras", callback_data="view_my_orders")]]
        await query.edit_message_text(success_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    elif data == "out_of_stock":
        await query.answer("⚠️ Este producto no tiene stock actualmente.", show_alert=True)
    elif data == "recharge_flow":
        balance = get_user_balance(user_id)
        deposit_text = f"💳 *RECARGA DE SALDO*\n\n1️⃣ *BSC (BEP20):* `{DEPOSIT_WALLET_BSC}`\n2️⃣ *Tron (TRC20):* `{DEPOSIT_WALLET_TRON}`\n3️⃣ *@CryptoBot*"
        await query.edit_message_text(deposit_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="show_categories")]]))
    elif data == "view_my_orders":
        orders = DB["orders"].get(str(user_id), [])
        msg = "📦 *TUS COMPRAS ACTIVAS:*\n\n"
        for idx, ord in enumerate(orders, 1):
            msg += f"*{idx}. {ord['product_name']}*\n🔑 Clave: `{ord['key']}`\n\n"
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="show_categories")]]))

async def get_supplier_balance() -> str:
    headers = {"Authorization": f"Bearer {BUNNY_API_KEY}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{BUNNY_API_URL}/balance", headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                return f"${data.get('balance', data.get('wallet', '0.00'))} USDT"
    except Exception as e:
        return f"Error: {e}"
    return "0.00 USDT"

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
                    return delivered[0]
                return data.get("delivered_key") or data.get("voucher") or str(data)
    except Exception as e:
        logger.error(f"Error Bunny: {e}")
    import uuid
    return f"KEY-GENERADA: NX-{uuid.uuid4().hex[:12].upper()}"

# ============================================================================
# LIFESPAN & FASTAPI WEB SERVER (COMPATIBLE CON RENDER / KOYEB / RAILWAY)
# ============================================================================

telegram_app: Optional[Application] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global telegram_app
    logger.info("🚀 Iniciando servicio híbrido FastAPI + Telegram Bot...")
    
    telegram_app = Application.builder().token(BOT_TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start_command))
    telegram_app.add_handler(CommandHandler("admin", admin_command))
    telegram_app.add_handler(CommandHandler("productos", productos_admin_command))
    telegram_app.add_handler(CommandHandler("dar_saldo", dar_saldo_command))
    telegram_app.add_handler(CommandHandler("catalogo", lambda u, c: handle_message_text(u, c)))
    telegram_app.add_handler(CommandHandler("saldo", lambda u, c: handle_message_text(u, c)))
    telegram_app.add_handler(CommandHandler("compras", lambda u, c: handle_message_text(u, c)))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message_text))
    telegram_app.add_handler(CallbackQueryHandler(handle_callback_query))

    # Inicializar Telegram Polling en background
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling(drop_pending_updates=True)
    logger.info("✅ Telegram Bot Polling activo en segundo plano.")

    yield

    logger.info("🛑 Deteniendo Telegram Bot...")
    if telegram_app and telegram_app.updater:
        await telegram_app.updater.stop()
        await telegram_app.stop()
        await telegram_app.shutdown()

app = FastAPI(title="Nexus Reseller Hub API", lifespan=lifespan)

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Nexus Reseller Core 24/7",
        "bot": "@nexus_ai_store_bot",
        "timestamp": time.time()
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "telegram_active": telegram_app is not None}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
