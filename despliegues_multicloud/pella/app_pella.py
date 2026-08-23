"""
=============================================================================
CYBERVAULT KEYS BOT - PELLA.APP EDITION (ULTRA-LIVIANO <25 MB RAM)
Bot: @cybervault_keys_bot
Plataforma: pella.app (Cuenta Pedro Gomez)
=============================================================================
"""

import os
import sys
import io
import json
import time
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
BUNNY_API_KEY = os.getenv("RESELLER_API_KEY", "YOUR_BUNNY_API_KEY")
BUNNY_API_URL = os.getenv("RESELLER_BASE_URL", "https://bhao.site/api/reseller/v1")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "1849945160"))

# Billeteras Pedro Gomez / Rafa
DEPOSIT_WALLET_BSC = os.getenv("DEPOSIT_WALLET_BSC", "0xe733e832e20cAE3a1e897F7F4A5B6e16934675C9")
DEPOSIT_WALLET_TRON = os.getenv("DEPOSIT_WALLET_TRON", "TZ3DYd7HNhnnSYUfris5Pqm66YmDugQ5Ch")
DEPOSIT_WALLET_SOL = os.getenv("DEPOSIT_WALLET_SOL", "cjwdWUXMtHgNU4dQmWEKPuyYLm4eonxpfyjhL6crCu4")
DEPOSIT_WALLET_BTC = os.getenv("DEPOSIT_WALLET_BTC", "bc1qt3s56f8h4crf69httj2snvseq5q6lskpnn5w64")

DB_FILE = "cybervault_db.json"

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

def tg_post(endpoint, payload):
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(f"{TELEGRAM_API}/{endpoint}", data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"TG Error {endpoint}:", e)
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

def handle_update(update):
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
                tg_post("sendMessage", {"chat_id": chat_id, "text": f"✅ Saldo acreditado a `{tid}`: `${n_bal:.2f} USDT`", "parse_mode": "Markdown"})
                tg_post("sendMessage", {"chat_id": tid, "text": f"💰 Recarga acreditada: `+${amt:.2f} USDT`\nSaldo: `${n_bal:.2f} USDT`", "parse_mode": "Markdown"})
                return

        if text == "/start" or text == "/catalogo":
            txt = (
                f"🔐 *¡Bienvenido a CyberVault Keys Store, {first_name}!* 🔐\n\n"
                f"🛡️ _VPNs, Seguridad Digital, Modelos de IA y Licencias Cloud._\n"
                f"👤 *ID:* `{u_id}` | 💰 *Saldo:* `${bal:.2f} USDT`\n\n"
                f"Elige una opción:"
            )
            kb = {
                "inline_keyboard": [
                    [{"text": "🔐 Catálogo de Seguridad & AI", "callback_data": "catalog"}],
                    [{"text": "💳 Mi Billetera / Recargar", "callback_data": "recharge"},
                     {"text": "📦 Mis Licencias", "callback_data": "orders"}],
                    [{"text": "💬 Soporte", "url": "https://t.me/Cctes001"}]
                ]
            }
            tg_post("sendMessage", {"chat_id": chat_id, "text": txt, "parse_mode": "Markdown", "reply_markup": kb})

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
            txt = f"🔐 *CYBERVAULT STORE* | Saldo: `${bal:.2f} USDT`"
            kb = {
                "inline_keyboard": [
                    [{"text": "🔐 Catálogo de Productos", "callback_data": "catalog"}],
                    [{"text": "💳 Recargar Saldo", "callback_data": "recharge"}, {"text": "📦 Mis Compras", "callback_data": "orders"}]
                ]
            }
            tg_post("editMessageText", {"chat_id": chat_id, "message_id": msg_id, "text": txt, "parse_mode": "Markdown", "reply_markup": kb})
        
        elif data == "catalog":
            prods = fetch_products()
            buttons = []
            for p in prods:
                cost = float(p.get("price_usdt") or p.get("your_cost") or 1.0)
                price = round(cost + 2.50, 2)
                buttons.append([{"text": f"🔐 {p['name']} — ${price:.2f}", "callback_data": f"p_{p['id']}"}])
            buttons.append([{"text": "🔙 Volver", "callback_data": "menu"}])
            tg_post("editMessageText", {"chat_id": chat_id, "message_id": msg_id, "text": "📂 *PRODUCTOS EN VIVO:*", "parse_mode": "Markdown", "reply_markup": {"inline_keyboard": buttons}})

        elif data.startswith("p_"):
            pid = int(data.replace("p_", ""))
            prods = fetch_products()
            p = next((x for x in prods if int(x["id"]) == pid), None)
            if p:
                cost = float(p.get("price_usdt") or p.get("your_cost") or 1.0)
                price = round(cost + 2.50, 2)
                txt = f"📦 *{p['name']}*\n\n💰 *Precio:* `${price:.2f} USDT`\n⏱️ *Duración:* `{p.get('duration', 'N/A')}`\n\nTu saldo: `${bal:.2f} USDT`"
                kb = {
                    "inline_keyboard": [
                        [{"text": f"⚡ Comprar Ahora (${price:.2f} USDT)", "callback_data": f"b_{p['id']}"}],
                        [{"text": "🔙 Volver", "callback_data": "catalog"}]
                    ]
                }
                tg_post("editMessageText", {"chat_id": chat_id, "message_id": msg_id, "text": txt, "parse_mode": "Markdown", "reply_markup": kb})

        elif data.startswith("b_"):
            pid = int(data.replace("b_", ""))
            prods = fetch_products()
            p = next((x for x in prods if int(x["id"]) == pid), None)
            if not p:
                return
            cost = float(p.get("price_usdt") or p.get("your_cost") or 1.0)
            price = round(cost + 2.50, 2)
            if bal < price:
                kb = {"inline_keyboard": [[{"text": "💳 Recargar Saldo", "callback_data": "recharge"}], [{"text": "🔙 Volver", "callback_data": f"p_{pid}"}]]}
                tg_post("editMessageText", {"chat_id": chat_id, "message_id": msg_id, "text": f"❌ *Saldo Insuficiente*\n\nPrecio: `${price:.2f}`\nTu saldo: `${bal:.2f}`", "parse_mode": "Markdown", "reply_markup": kb})
                return
            
            n_bal = bal - price
            if "balances" not in DB:
                DB["balances"] = {}
            DB["balances"][str(u_id)] = round(n_bal, 2)
            
            # Despachar orden
            headers = {"Authorization": f"Bearer {BUNNY_API_KEY}", "Content-Type": "application/json"}
            key_del = f"CYBER-KEY-{int(time.time())}"
            try:
                req = urllib.request.Request(f"{BUNNY_API_URL}/order", data=json.dumps({"product_id": pid, "quantity": 1}).encode('utf-8'), headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=15) as resp:
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

            txt = f"🎉 *¡COMPRA EXITOSA!* 🎉\n\n📦 *{p['name']}*\n🔑 *LICENCIA:*\n```\n{key_del}\n```\n\n💳 Saldo restante: `${n_bal:.2f} USDT`"
            tg_post("editMessageText", {"chat_id": chat_id, "message_id": msg_id, "text": txt, "parse_mode": "Markdown", "reply_markup": {"inline_keyboard": [[{"text": "🛍️ Catálogo", "callback_data": "catalog"}]]}})

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
                txt = "📦 *TUS LICENCIAS:*\n\n"
                for idx, o in enumerate(ords, 1):
                    txt += f"*{idx}. {o.get('product')}*\n🔑 `{o.get('key')}`\n\n"
                tg_post("editMessageText", {"chat_id": chat_id, "message_id": msg_id, "text": txt, "parse_mode": "Markdown", "reply_markup": {"inline_keyboard": [[{"text": "🔙 Volver", "callback_data": "menu"}]]}})

def polling_worker():
    offset = 0
    print("⚡ Iniciando Polling ultra-liviano para CyberVault Bot...")
    tg_post("deleteWebhook", {"drop_pending_updates": True})
    while True:
        try:
            res = tg_post("getUpdates", {"offset": offset, "timeout": 20})
            if res and res.get("ok"):
                for upd in res.get("result", []):
                    offset = upd["update_id"] + 1
                    handle_update(upd)
        except Exception as e:
            print("Poll loop error:", e)
        time.sleep(1)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "online", "service": "CyberVault Pella 24/7", "bot": "@cybervault_keys_bot"}).encode('utf-8'))

def run_server():
    port = int(os.getenv("PORT", "3000"))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"🌍 Servidor HTTP Health activo en puerto {port}...")
    server.serve_forever()

if __name__ == "__main__":
    t = threading.Thread(target=polling_worker, daemon=True)
    t.start()
    run_server()
