"""
=============================================================================
DEVCORE PRO BOT - TELEBOTHOST EDITION (24/7 DEDICATED HOSTING)
Bot: @devcore_pro_bot
Plataforma: console.telebothost.com (Cuenta Pedro Gomez)
=============================================================================
"""

import os
import sys
import io
import json
import time
import urllib.request
import urllib.parse

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8918777311:AAFXqk2CSj_y77WtG3hyQ50WAtHCENiZFmE")
BUNNY_API_KEY = os.getenv("RESELLER_API_KEY", "bai_sk_4a557cbb3c136090682510a41a13585560feff74e56eaa0e")
BUNNY_API_URL = os.getenv("RESELLER_BASE_URL", "https://bhao.site/api/reseller/v1")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "1849945160"))

# Billeteras Personales de Pedro Gomez / Rafa
DEPOSIT_WALLET_BSC = os.getenv("DEPOSIT_WALLET_BSC", "0xe733e832e20cAE3a1e897F7F4A5B6e16934675C9")
DEPOSIT_WALLET_TRON = os.getenv("DEPOSIT_WALLET_TRON", "TZ3DYd7HNhnnSYUfris5Pqm66YmDugQ5Ch")
DEPOSIT_WALLET_SOL = os.getenv("DEPOSIT_WALLET_SOL", "cjwdWUXMtHgNU4dQmWEKPuyYLm4eonxpfyjhL6crCu4")
DEPOSIT_WALLET_BTC = os.getenv("DEPOSIT_WALLET_BTC", "bc1qt3s56f8h4crf69httj2snvseq5q6lskpnn5w64")

DB_FILE = "devcore_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"balances": {}, "orders": {}}

def save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

DB = load_db()

def get_bal(uid):
    return float(DB.get("balances", {}).get(str(uid), 0.0))

def set_bal(uid, amt):
    if "balances" not in DB:
        DB["balances"] = {}
    DB["balances"][str(uid)] = round(amt, 2)
    save_db(DB)

def fetch_products():
    headers = {"Authorization": f"Bearer {BUNNY_API_KEY}", "Content-Type": "application/json"}
    try:
        req = urllib.request.Request(f"{BUNNY_API_URL}/products", headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            raw = data.get("products", [])
            prods = []
            for p in raw:
                cost = float(p.get("price_usdt") or p.get("your_cost") or 1.0)
                retail = round(cost + 2.50, 2) if cost > 1.0 else round(cost + 1.50, 2)
                prods.append({
                    "id": int(p.get("id")),
                    "name": p.get("name", "Producto"),
                    "desc": p.get("description", "").replace("[emoji:1]", "•"),
                    "price": retail,
                    "cost": cost,
                    "stock": p.get("stock", 0),
                    "duration": p.get("duration", "N/A")
                })
            return prods
    except Exception as e:
        print("Error Bunny:", e)
        return []

def get_main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💻 Ver Herramientas Dev & Cloud", callback_data="catalog")],
        [InlineKeyboardButton("💳 Mi Saldo / Recargar", callback_data="recharge"),
         InlineKeyboardButton("📦 Mis Compras", callback_data="orders")],
        [InlineKeyboardButton("💬 Soporte", url="https://t.me/Cctes001")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    bal = get_bal(u.id)
    txt = (
        f"💻 *¡Bienvenido a DevCore Pro Store, {u.first_name}!* 💻\n\n"
        f"⚡ _Plataforma de Dev Tools, IDEs, Modelos y Cuentas Premium._\n"
        f"👤 *ID:* `{u.id}` | 💰 *Saldo:* `${bal:.2f} USDT`\n\n"
        f"Elige una opción:"
    )
    if update.message:
        await update.message.reply_text(txt, parse_mode="Markdown", reply_markup=get_main_kb())

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    prods = fetch_products()
    await update.message.reply_text(f"👑 *DEVCORE ADMIN*\n\nAdmin: `{ADMIN_ID}`\nProductos en vivo: `{len(prods)}`\n\n• `/dar_saldo <id> <monto>`", parse_mode="Markdown")

async def dar_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID or len(context.args) < 2:
        return
    t_id, amt = int(context.args[0]), float(context.args[1])
    n_bal = get_bal(t_id) + amt
    set_bal(t_id, n_bal)
    await update.message.reply_text(f"✅ Saldo de `{t_id}`: `${n_bal:.2f} USDT`")

async def cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    u_id = q.from_user.id
    bal = get_bal(u_id)

    if q.data == "menu":
        await q.edit_message_text(f"💻 *DEVCORE PRO* | Saldo: `${bal:.2f} USDT`", parse_mode="Markdown", reply_markup=get_main_kb())
    elif q.data == "catalog":
        prods = fetch_products()
        btns = [[InlineKeyboardButton(f"⚡ {p['name']} — ${p['price']:.2f}", callback_data=f"p_{p['id']}")] for p in prods]
        btns.append([InlineKeyboardButton("🔙 Volver", callback_data="menu")])
        await q.edit_message_text("📂 *PRODUCTOS DISPONIBLES:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(btns))
    elif q.data.startswith("p_"):
        pid = int(q.data.replace("p_", ""))
        p = next((x for x in fetch_products() if x["id"] == pid), None)
        if p:
            txt = f"📦 *{p['name']}*\n\n📝 {p['desc']}\n\n💰 *Precio:* `${p['price']:.2f} USDT`\n⏱️ *Duración:* `{p['duration']}`\n\nTu saldo: `${bal:.2f} USDT`"
            kb = [
                [InlineKeyboardButton(f"⚡ Comprar Ahora (${p['price']:.2f} USDT)", callback_data=f"b_{p['id']}")],
                [InlineKeyboardButton("🔙 Volver al Catálogo", callback_data="catalog")]
            ]
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    elif q.data.startswith("b_"):
        pid = int(q.data.replace("b_", ""))
        p = next((x for x in fetch_products() if x["id"] == pid), None)
        if not p:
            return
        if bal < p["price"]:
            kb = [[InlineKeyboardButton("💳 Recargar", callback_data="recharge")], [InlineKeyboardButton("🔙 Volver", callback_data=f"p_{pid}")]]
            await q.edit_message_text(f"❌ *Saldo Insuficiente*\n\nPrecio: `${p['price']:.2f}`\nTu saldo: `${bal:.2f}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
            return
        
        await q.edit_message_text("⏳ *Despachando licencia...*", parse_mode="Markdown")
        n_bal = bal - p["price"]
        set_bal(u_id, n_bal)
        
        headers = {"Authorization": f"Bearer {BUNNY_API_KEY}", "Content-Type": "application/json"}
        key_del = f"DEVCORE-KEY-{int(time.time())}"
        try:
            req = urllib.request.Request(f"{BUNNY_API_URL}/order", data=json.dumps({"product_id": pid, "quantity": 1}).encode('utf-8'), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=15) as resp:
                d = json.loads(resp.read().decode())
                key_del = d.get("delivered", [d.get("delivered_key", str(d))])[0]
        except Exception as e:
            print("Order error:", e)
        
        if "orders" not in DB:
            DB["orders"] = {}
        if str(u_id) not in DB["orders"]:
            DB["orders"][str(u_id)] = []
        DB["orders"][str(u_id)].append({"product": p["name"], "key": key_del, "date": time.strftime("%Y-%m-%d %H:%M")})
        save_db(DB)

        txt = f"🎉 *¡COMPRA EXITOSA!* 🎉\n\n📦 *{p['name']}*\n🔑 *LICENCIA:*\n```\n{key_del}\n```\n\n💳 Saldo restante: `${n_bal:.2f} USDT`"
        await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛍️ Catálogo", callback_data="catalog")]]))
    elif q.data == "recharge":
        txt = (
            f"💳 *RECARGA DE SALDO (USDT / CRIPTO)*\n\n"
            f"👤 ID: `{u_id}`\n\n"
            f"🟡 *USDT BEP-20 (BNB Smart Chain):*\n`{DEPOSIT_WALLET_BSC}`\n\n"
            f"🔴 *USDT TRC-20 (Tron):*\n`{DEPOSIT_WALLET_TRON}`\n\n"
            f"🟣 *Solana (SOL/USDT):*\n`{DEPOSIT_WALLET_SOL}`\n\n"
            f"🟠 *Bitcoin (BTC):*\n`{DEPOSIT_WALLET_BTC}`\n\n"
            f"Envía comprobante a @Cctes001."
        )
        kb = [[InlineKeyboardButton("🤖 @CryptoBot", url="https://t.me/CryptoBot")],
              [InlineKeyboardButton("💬 Admin", url="https://t.me/Cctes001")],
              [InlineKeyboardButton("🔙 Volver", callback_data="menu")]]
        await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    elif q.data == "orders":
        ords = DB.get("orders", {}).get(str(u_id), [])
        if not ords:
            await q.edit_message_text("📦 Sin compras aún.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛍️ Catálogo", callback_data="catalog")]]))
        else:
            txt = "📦 *TUS COMPRAS:*\n\n"
            for idx, o in enumerate(ords, 1):
                txt += f"*{idx}. {o.get('product')}*\n🔑 `{o.get('key')}`\n\n"
            await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="menu")]]))

def main():
    print("🚀 Iniciando DevCore Pro Bot en TeleBotHost...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("dar_saldo", dar_saldo))
    app.add_handler(CallbackQueryHandler(cb_handler))
    print("✅ Polling activo 24/7.")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
