"""
=============================================================================
PYTHONANYWHERE WSGI / FLASK ENGINE (FREE TIER COMPATIBLE)
Alojamiento 100% gratuito en: <tu_usuario>.pythonanywhere.com
Compatible con whitelist de Telegram API y entrega dinámica de licencias.
=============================================================================
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
from flask import Flask, request, jsonify

app = Flask(__name__)

# Credenciales y Configuración
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8870399329:AAG9Co0upODc7UJ_QgodmgaQiORNPc9jTX4")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
BUNNY_API_KEY = os.getenv("RESELLER_API_KEY", "bai_sk_4a557cbb3c136090682510a41a13585560feff74e56eaa0e")
BUNNY_API_URL = os.getenv("RESELLER_BASE_URL", "https://bhao.site/api/reseller/v1")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "1849945160"))

# Billeteras de Cobro
DEPOSIT_WALLET_BSC = os.getenv("DEPOSIT_WALLET_BSC", "0xe733e832e20cAE3a1e897F7F4A5B6e16934675C9")
DEPOSIT_WALLET_TRON = os.getenv("DEPOSIT_WALLET_TRON", "TZ3DYd7HNhnnSYUfris5Pqm66YmDugQ5Ch")
DEPOSIT_WALLET_SOL = os.getenv("DEPOSIT_WALLET_SOL", "cjwdWUXMtHgNU4dQmWEKPuyYLm4eonxpfyjhL6crCu4")
DEPOSIT_WALLET_BTC = os.getenv("DEPOSIT_WALLET_BTC", "bc1qt3s56f8h4crf69httj2snvseq5q6lskpnn5w64")

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pa_db.json")

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

def tg_post(method, payload):
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(f"{TELEGRAM_API}/{method}", data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"TG Error {method}: {e}")
        return None

def fetch_products():
    headers = {"Authorization": f"Bearer {BUNNY_API_KEY}", "Content-Type": "application/json"}
    try:
        req = urllib.request.Request(f"{BUNNY_API_URL}/products", headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data.get("products", [])
    except Exception as e:
        print("Bunny Error:", e)
        return []

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "service": "PythonAnywhere Reseller Gateway",
        "bot": "@nova_ai_keys_bot"
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "engine": "Flask/WSGI on PythonAnywhere"})

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    update = request.get_json(force=True, silent=True)
    if not update:
        return "OK", 200

    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        u_id = msg["from"]["id"]
        text = msg.get("text", "").strip()
        first_name = msg["from"].get("first_name", "Cliente")
        bal = float(DB.get("balances", {}).get(str(u_id), 0.0))

        if text.startswith("/dar_saldo") and u_id == ADMIN_ID:
            parts = text.split()
            if len(parts) >= 3:
                tid, amt = parts[1], float(parts[2])
                if "balances" not in DB:
                    DB["balances"] = {}
                n_bal = float(DB["balances"].get(str(tid), 0.0)) + amt
                DB["balances"][str(tid)] = round(n_bal, 2)
                save_db(DB)
                tg_post("sendMessage", {"chat_id": chat_id, "text": f"✅ Saldo asignado a `{tid}`: `${n_bal:.2f} USDT`", "parse_mode": "Markdown"})
                tg_post("sendMessage", {"chat_id": tid, "text": f"💰 Recarga acreditada: `+${amt:.2f} USDT`\nSaldo: `${n_bal:.2f} USDT`", "parse_mode": "Markdown"})
                return "OK", 200

        if text in ["/start", "/catalogo", "Catálogo"]:
            welcome_text = (
                f"⚡ *¡Bienvenido a Nova AI Keys Store, {first_name}!* ⚡\n\n"
                f"🔥 *Catálogo Oficial conectado en vivo a Bunny Tools.*\n"
                f"🚀 _Entrega de cuentas y licencias en 1 segundo vía API._\n\n"
                f"👤 *Tu ID:* `{u_id}`\n"
                f"💰 *Tu Saldo Disponible:* `${bal:.2f} USDT`\n\n"
                f"Elige una opción:"
            )
            kb = {
                "inline_keyboard": [
                    [{"text": "🛍️ Ver Catálogo en Vivo", "callback_data": "catalog"}],
                    [{"text": "💳 Mi Saldo / Recargar", "callback_data": "recharge"},
                     {"text": "📦 Mis Compras", "callback_data": "orders"}],
                    [{"text": "💬 Soporte Técnico", "url": "https://t.me/Cctes001"}]
                ]
            }
            tg_post("sendMessage", {"chat_id": chat_id, "text": welcome_text, "parse_mode": "Markdown", "reply_markup": kb})

    elif "callback_query" in update:
        cq = update["callback_query"]
        cq_id = cq["id"]
        chat_id = cq["message"]["chat"]["id"]
        msg_id = cq["message"]["message_id"]
        u_id = cq["from"]["id"]
        data = cq["data"]
        bal = float(DB.get("balances", {}).get(str(u_id), 0.0))

        tg_post("answerCallbackQuery", {"callback_query_id": cq_id})

        if data == "menu":
            tg_post("editMessageText", {
                "chat_id": chat_id, "message_id": msg_id,
                "text": f"⚡ *NOVA AI STORE — MENÚ*\n\n💰 Saldo: `${bal:.2f} USDT`",
                "parse_mode": "Markdown",
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": "🛍️ Catálogo", "callback_data": "catalog"}],
                        [{"text": "💳 Recargar Saldo", "callback_data": "recharge"}, {"text": "📦 Mis Compras", "callback_data": "orders"}]
                    ]
                }
            })

        elif data == "catalog":
            prods = fetch_products()
            buttons = []
            for p in prods:
                cost = float(p.get("price_usdt") or p.get("your_cost") or 1.0)
                price = round(cost + 2.50, 2)
                icon = "🟢" if p.get("stock") != 0 else "🔴"
                buttons.append([{"text": f"{icon} {p['name']} — ${price:.2f}", "callback_data": f"p_{p['id']}"}])
            buttons.append([{"text": "🔙 Volver", "callback_data": "menu"}])
            tg_post("editMessageText", {
                "chat_id": chat_id, "message_id": msg_id,
                "text": "📂 *CATÁLOGO DE PRODUCTOS EN VIVO:*",
                "parse_mode": "Markdown",
                "reply_markup": {"inline_keyboard": buttons}
            })

        elif data.startswith("p_"):
            pid = int(data.replace("p_", ""))
            prods = fetch_products()
            p = next((x for x in prods if int(x["id"]) == pid), None)
            if p:
                cost = float(p.get("price_usdt") or p.get("your_cost") or 1.0)
                price = round(cost + 2.50, 2)
                txt = f"📦 *{p['name']}*\n\n📝 {p.get('description', '')}\n\n💰 *Precio:* `${price:.2f} USDT`\n⏱️ *Duración:* `{p.get('duration', 'N/A')}`\n\nTu saldo: `${bal:.2f} USDT`"
                kb = {
                    "inline_keyboard": [
                        [{"text": f"⚡ Comprar Ahora (${price:.2f} USDT)", "callback_data": f"b_{p['id']}"}],
                        [{"text": "🔙 Volver al Catálogo", "callback_data": "catalog"}]
                    ]
                }
                tg_post("editMessageText", {"chat_id": chat_id, "message_id": msg_id, "text": txt, "parse_mode": "Markdown", "reply_markup": kb})

        elif data.startswith("b_"):
            pid = int(data.replace("b_", ""))
            prods = fetch_products()
            p = next((x for x in prods if int(x["id"]) == pid), None)
            if not p:
                return "OK", 200
            cost = float(p.get("price_usdt") or p.get("your_cost") or 1.0)
            price = round(cost + 2.50, 2)
            if bal < price:
                kb = {"inline_keyboard": [[{"text": "💳 Recargar Saldo", "callback_data": "recharge"}], [{"text": "🔙 Volver", "callback_data": f"p_{pid}"}]]}
                tg_post("editMessageText", {"chat_id": chat_id, "message_id": msg_id, "text": f"❌ *Saldo Insuficiente*\n\nPrecio: `${price:.2f}`\nTu saldo: `${bal:.2f}`", "parse_mode": "Markdown", "reply_markup": kb})
                return "OK", 200

            n_bal = bal - price
            if "balances" not in DB:
                DB["balances"] = {}
            DB["balances"][str(u_id)] = round(n_bal, 2)

            headers = {"Authorization": f"Bearer {BUNNY_API_KEY}", "Content-Type": "application/json"}
            key_del = f"PA-KEY-{int(time.time())}"
            try:
                req_order = urllib.request.Request(f"{BUNNY_API_URL}/order", data=json.dumps({"product_id": pid, "quantity": 1}).encode("utf-8"), headers=headers, method="POST")
                with urllib.request.urlopen(req_order, timeout=15) as resp:
                    d = json.loads(resp.read().decode())
                    key_del = d.get("delivered", [d.get("delivered_key", str(d))])[0]
            except Exception as e:
                print("Order err:", e)

            if "orders" not in DB:
                DB["orders"] = {}
            if str(u_id) not in DB["orders"]:
                DB["orders"][str(u_id)] = []
            DB["orders"][str(u_id)].append({"product": p["name"], "key": key_del, "date": time.strftime("%Y-%m-%d %H:%M")})
            save_db(DB)

            txt = f"🎉 *¡COMPRA EXITOSA!* 🎉\n\n📦 *{p['name']}*\n🔑 *TU LICENCIA:*\n```\n{key_del}\n```\n\n💳 Saldo restante: `${n_bal:.2f} USDT`"
            tg_post("editMessageText", {"chat_id": chat_id, "message_id": msg_id, "text": txt, "parse_mode": "Markdown", "reply_markup": {"inline_keyboard": [[{"text": "🛍️ Ver Catálogo", "callback_data": "catalog"}]]}})

        elif data == "recharge":
            txt = (
                f"💳 *RECARGA DE SALDO CRIPTO*\n\n"
                f"👤 ID: `{u_id}`\n\n"
                f"🟡 *USDT BEP-20 (BSC):*\n`{DEPOSIT_WALLET_BSC}`\n\n"
                f"🔴 *USDT TRC-20 (Tron):*\n`{DEPOSIT_WALLET_TRON}`\n\n"
                f"🟣 *Solana (SOL/USDT):*\n`{DEPOSIT_WALLET_SOL}`\n\n"
                f"🟠 *Bitcoin (BTC):*\n`{DEPOSIT_WALLET_BTC}`\n\n"
                f"Envía comprobante a @Cctes001."
            )
            kb = {"inline_keyboard": [[{"text": "🤖 @CryptoBot", "url": "https://t.me/CryptoBot"}], [{"text": "🔙 Volver", "callback_data": "menu"}]]}
            tg_post("editMessageText", {"chat_id": chat_id, "message_id": msg_id, "text": txt, "parse_mode": "Markdown", "reply_markup": kb})

        elif data == "orders":
            ords = DB.get("orders", {}).get(str(u_id), [])
            if not ords:
                tg_post("editMessageText", {"chat_id": chat_id, "message_id": msg_id, "text": "📦 Sin compras aún.", "reply_markup": {"inline_keyboard": [[{"text": "🛍️ Catálogo", "callback_data": "catalog"}]]}})
            else:
                txt = "📦 *TUS COMPRAS ACTIVAS:*\n\n"
                for idx, o in enumerate(ords, 1):
                    txt += f"*{idx}. {o.get('product')}*\n🔑 `{o.get('key')}`\n\n"
                tg_post("editMessageText", {"chat_id": chat_id, "message_id": msg_id, "text": txt, "parse_mode": "Markdown", "reply_markup": {"inline_keyboard": [[{"text": "🔙 Volver", "callback_data": "menu"}]]}})

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
