"""
=============================================================================
NEXUS RESELLER HUB - CORE ENGINE PRIVADO (PROTEGIDO EN DATASET)
Este archivo se almacena EXCLUSIVAMENTE dentro de tu Dataset Privado de Hugging Face.
Nadie desde el Space público puede ver el código fuente, márgenes ni endpoints.
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

logging.basicConfig(format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger("StealthResellerEngine")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuración y Secretos (Inyectados desde HF Space Secrets)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8870399329:AAG9Co0upODc7UJ_QgodmgaQiORNPc9jTX4")
BUNNY_API_KEY = os.getenv("RESELLER_API_KEY", "bai_sk_4a557cbb3c136090682510a41a13585560feff74e56eaa0e")
BUNNY_API_URL = os.getenv("RESELLER_BASE_URL", "https://bhao.site/api/reseller/v1")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "1849945160"))

# Billeteras Personales de Cobro
DEPOSIT_WALLET_BSC = os.getenv("DEPOSIT_WALLET_BSC", "0xe733e832e20cAE3a1e897F7F4A5B6e16934675C9")
DEPOSIT_WALLET_TRON = os.getenv("DEPOSIT_WALLET_TRON", "TZ3DYd7HNhnnSYUfris5Pqm66YmDugQ5Ch")
DEPOSIT_WALLET_BTC = os.getenv("DEPOSIT_WALLET_BTC", "bc1qt3s56f8h4crf69httj2snvseq5q6lskpnn5w64")
DEPOSIT_WALLET_SOL = os.getenv("DEPOSIT_WALLET_SOL", "cjwdWUXMtHgNU4dQmWEKPuyYLm4eonxpfyjhL6crCu4")

# Detección de URL pública en Hugging Face
SPACE_HOST = os.getenv("SPACE_HOST", "")
HF_SPACE_URL = f"https://{SPACE_HOST}" if SPACE_HOST else os.getenv("WEBHOOK_URL", "")
RUN_MODE = os.getenv("RUN_MODE", "webhook" if HF_SPACE_URL else "polling").lower()

DATA_DB_PATH = os.path.join(BASE_DIR, "stealth_db.json")

def load_db():
    if os.path.exists(DATA_DB_PATH):
        try:
            with open(DATA_DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"balances": {}, "orders": {}, "users": {}}

def save_db(data):
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

def record_user_order(user_id: int, order_data: dict):
    u_str = str(user_id)
    if "orders" not in DB:
        DB["orders"] = {}
    if u_str not in DB["orders"]:
        DB["orders"][u_str] = []
    DB["orders"][u_str].append(order_data)
    save_db(DB)

# Catálogo Bunny Dinámico en Vivo
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
    else:
        return round(cost + 3.50, 2)

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
                        "requires_email": p.get("requires_email", False)
                    })
                CACHE_PRODUCTS = processed
                CACHE_TIMESTAMP = now
                return processed
    except Exception as e:
        logger.error(f"Error conectando con Bunny API: {e}")
    return CACHE_PRODUCTS

def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Ver Catálogo de Productos", callback_data="show_catalog")],
        [InlineKeyboardButton("💳 Mi Billetera / Recargar", callback_data="recharge_flow"),
         InlineKeyboardButton("📦 Mis Licencias", callback_data="view_orders")],
        [InlineKeyboardButton("💬 Soporte y Atención", url="https://t.me/Cctes001")]
    ])

def get_recharge_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🟡 USDT BEP-20 (BNB Smart Chain)", callback_data="w_bep20"),
         InlineKeyboardButton("🔴 USDT TRC-20 (Tron)", callback_data="w_trc20")],
        [InlineKeyboardButton("🟣 Solana (SOL / USDT)", callback_data="w_sol"),
         InlineKeyboardButton("🟠 Bitcoin (BTC)", callback_data="w_btc")],
        [InlineKeyboardButton("🤖 Pagar con @CryptoBot", url="https://t.me/CryptoBot")],
        [InlineKeyboardButton("🔙 Volver al Menú", callback_data="main_menu")]
    ])

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    balance = get_user_balance(user.id)
    text = (
        f"⚡ *¡Bienvenido a Nova AI Keys Hub, {user.first_name}!* ⚡\n\n"
        f"🔥 *Catálogo 100% dinámico y sincronizado en tiempo real.*\n"
        f"🚀 _Entrega de cuentas y licencias en 1 segundo vía API._\n\n"
        f"👤 *Tu ID:* `{user.id}`\n"
        f"💰 *Tu Saldo Disponible:* `${balance:.2f} USDT`\n\n"
        f"Selecciona una opción para comenzar:"
    )
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    prods = await fetch_live_products(force_refresh=True)
    msg = (
        f"👑 *PANEL ADMINISTRADOR (STEALTH ENGINE 24/7)*\n\n"
        f"👤 *Admin:* `{ADMIN_ID}` (@Cctes001)\n"
        f"📦 *Productos Activos:* `{len(prods)}`\n"
        f"👥 *Clientes en DB:* `{len(DB.get('users', {}))}`\n\n"
        f"• `/dar_saldo <id> <monto>`\n"
        f"• `/productos`"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def dar_saldo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID or len(context.args) < 2:
        return
    try:
        t_id, amt = int(context.args[0]), float(context.args[1])
        new_bal = get_user_balance(t_id) + amt
        set_user_balance(t_id, new_bal)
        await update.message.reply_text(f"✅ Saldo acreditado a `{t_id}`: `${new_bal:.2f} USDT`", parse_mode="Markdown")
        try:
            await context.bot.send_message(chat_id=t_id, text=f"🎉 *¡Recarga acreditada!*\nHas recibido: `+${amt:.2f} USDT`\nSaldo actual: `${new_bal:.2f} USDT`", parse_mode="Markdown")
        except Exception:
            pass
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    balance = get_user_balance(user_id)

    if data == "main_menu":
        await query.edit_message_text(f"⚡ *NOVA AI STORE — MENÚ*\n\n👤 ID: `{user_id}`\n💰 Saldo: `${balance:.2f} USDT`", parse_mode="Markdown", reply_markup=get_main_keyboard())
    elif data == "show_catalog":
        products = await fetch_live_products()
        buttons = []
        for p in products:
            stock_icon = "🟢" if p["stock"] != 0 else "🔴"
            buttons.append([InlineKeyboardButton(f"{stock_icon} {p['name']} — ${p['retail_price']:.2f}", callback_data=f"p_{p['id']}")])
        buttons.append([InlineKeyboardButton("🔙 Volver al Menú", callback_data="main_menu")])
        await query.edit_message_text("📂 *CATÁLOGO DE PRODUCTOS EN VIVO:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))
    elif data.startswith("p_"):
        prod_id = int(data.replace("p_", ""))
        products = await fetch_live_products()
        p = next((x for x in products if x["id"] == prod_id), None)
        if p:
            stock_txt = f"🟢 Disponible ({p['stock']})" if p['stock'] != 0 else "🔴 Agotado"
            txt = f"📦 *{p['name']}*\n\n📝 {p['description']}\n\n💰 *Precio:* `${p['retail_price']:.2f} USDT`\n⏱️ *Duración:* `{p['duration']}`\n📊 *Stock:* `{stock_txt}`\n\nTu saldo: `${balance:.2f} USDT`"
            kb = [
                [InlineKeyboardButton(f"⚡ Comprar Ahora (${p['retail_price']:.2f} USDT)", callback_data=f"b_{p['id']}")],
                [InlineKeyboardButton("🔙 Volver al Catálogo", callback_data="show_catalog")]
            ]
            await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    elif data.startswith("b_"):
        prod_id = int(data.replace("b_", ""))
        products = await fetch_live_products()
        p = next((x for x in products if x["id"] == prod_id), None)
        if not p:
            return
        if balance < p["retail_price"]:
            kb = [[InlineKeyboardButton("💳 Recargar Saldo", callback_data="recharge_flow")], [InlineKeyboardButton("🔙 Volver", callback_data=f"p_{prod_id}")]]
            await query.edit_message_text(f"❌ *Saldo Insuficiente*\n\nPrecio: `${p['retail_price']:.2f} USDT`\nTu saldo: `${balance:.2f} USDT`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
            return
        
        await query.edit_message_text("⏳ *Despachando orden con Bunny Tools en 1 segundo...*", parse_mode="Markdown")
        new_bal = balance - p["retail_price"]
        set_user_balance(user_id, new_bal)
        
        headers = {"Authorization": f"Bearer {BUNNY_API_KEY}", "Content-Type": "application/json"}
        key_delivered = f"KEY-VOUCHER-{int(time.time())}"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(f"{BUNNY_API_URL}/order", json={"product_id": prod_id, "quantity": 1}, headers=headers)
                if res.status_code in [200, 201]:
                    d = res.json()
                    deliv = d.get("delivered", [])
                    key_delivered = deliv[0] if deliv else d.get("delivered_key", str(d))
        except Exception as e:
            logger.error(f"Error despachando orden: {e}")
        
        record_user_order(user_id, {"product": p["name"], "key": key_delivered, "date": time.strftime("%Y-%m-%d %H:%M")})
        res_txt = f"🎉 *¡COMPRA COMPLETADA CON ÉXITO!* 🎉\n\n📦 *Producto:* {p['name']}\n💰 *Debitado:* `${p['retail_price']:.2f} USDT`\n\n🔑 *TU LICENCIA / CREDENCIAL:*\n```\n{key_delivered}\n```\n\n💳 Saldo restante: `${new_bal:.2f} USDT`"
        await query.edit_message_text(res_txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛍️ Ver Catálogo", callback_data="show_catalog")]]))
    elif data == "recharge_flow":
        txt = f"💳 *BILLETERA & RECARGA DE SALDO*\n\n👤 ID: `{user_id}`\n💰 Saldo: `${balance:.2f} USDT`\n\nSelecciona la red de depósito:"
        await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=get_recharge_keyboard())
    elif data == "w_bep20":
        txt = f"🟡 *USDT (BNB SMART CHAIN - BEP20)*\n\n`{DEPOSIT_WALLET_BSC}`\n\nEnvía comprobante con tu ID `{user_id}` a @Cctes001 para acreditar."
        await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="recharge_flow")]]))
    elif data == "w_trc20":
        txt = f"🔴 *USDT (TRON - TRC20)*\n\n`{DEPOSIT_WALLET_TRON}`\n\nEnvía comprobante con tu ID `{user_id}` a @Cctes001 para acreditar."
        await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="recharge_flow")]]))
    elif data == "w_sol":
        txt = f"🟣 *SOLANA (SOL / USDT SPL)*\n\n`{DEPOSIT_WALLET_SOL}`\n\nEnvía comprobante con tu ID `{user_id}` a @Cctes001."
        await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="recharge_flow")]]))
    elif data == "w_btc":
        txt = f"🟠 *BITCOIN (BTC)*\n\n`{DEPOSIT_WALLET_BTC}`\n\nEnvía comprobante con tu ID `{user_id}` a @Cctes001."
        await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="recharge_flow")]]))
    elif data == "view_orders":
        orders = DB.get("orders", {}).get(str(user_id), [])
        if not orders:
            await query.edit_message_text("📦 No tienes compras registradas aún.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛍️ Catálogo", callback_data="show_catalog")]]))
        else:
            txt = "📦 *TUS LICENCIAS ACTIVAS:*\n\n"
            for idx, o in enumerate(orders, 1):
                txt += f"*{idx}. {o.get('product')}*\n🔑 `{o.get('key')}`\n📅 {o.get('date')}\n\n"
            await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="main_menu")]]))

# Lifespan
telegram_app: Optional[Application] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global telegram_app
    logger.info("🚀 Iniciando Motor Reseller Sigiloso...")
    telegram_app = Application.builder().token(BOT_TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start_command))
    telegram_app.add_handler(CommandHandler("admin", admin_command))
    telegram_app.add_handler(CommandHandler("dar_saldo", dar_saldo_command))
    telegram_app.add_handler(CommandHandler("catalogo", lambda u, c: start_command(u, c)))
    telegram_app.add_handler(CallbackQueryHandler(handle_callback_query))

    await telegram_app.initialize()
    await telegram_app.start()

    if HF_SPACE_URL and RUN_MODE == "webhook":
        wh_url = f"{HF_SPACE_URL}/webhook"
        logger.info(f"🌐 Seteando Webhook en HF Space: {wh_url}")
        await telegram_app.bot.set_webhook(url=wh_url, drop_pending_updates=True)
    else:
        logger.info("⚡ Iniciando Polling...")
        await telegram_app.bot.delete_webhook(drop_pending_updates=True)
        await telegram_app.updater.start_polling(drop_pending_updates=True)

    yield

    if telegram_app:
        if telegram_app.updater and telegram_app.updater.running:
            await telegram_app.updater.stop()
        await telegram_app.stop()
        await telegram_app.shutdown()

app = FastAPI(title="Nova AI Keys Hub (Stealth Edition)", lifespan=lifespan)

@app.post("/webhook")
async def webhook_endpoint(request: Request):
    try:
        data = await request.json()
        if telegram_app:
            update = Update.de_json(data, telegram_app.bot)
            await telegram_app.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head><title>Nova AI Keys Store</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 60px; background: #0b0f19; color: #f8fafc;">
            <h1 style="color: #6366f1;">⚡ Nova AI Keys Hub 24/7</h1>
            <p>Servidor activo en Hugging Face Spaces (16 GB RAM) con Despacho Automatizado.</p>
            <p><a style="color: #38bdf8; text-decoration: none; font-weight: bold;" href="https://t.me/nova_ai_keys_bot" target="_blank">🤖 Abrir Tienda en Telegram (@nova_ai_keys_bot)</a></p>
        </body>
    </html>
    """

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Nova AI Keys Hub Stealth", "telegram_bot": "@nova_ai_keys_bot"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run("bot_core:app", host="0.0.0.0", port=port)
