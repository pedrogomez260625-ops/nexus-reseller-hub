"""
Nexus Reseller Core - Anonymous FastAPI Entry Point
System: Ghost Reseller Gateway
"""

from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional
from ghost_reseller.config import settings
from ghost_reseller.services.supplier_client import SupplierClient
from ghost_reseller.services.wallet_ledger import WalletLedger

app = FastAPI(
    title=settings.SYSTEM_NAME,
    version=settings.VERSION,
    description="Nexus Reseller Gateway API"
)

supplier = SupplierClient(api_key=settings.RESELLER_API_KEY, base_url=settings.RESELLER_BASE_URL, default_markup_usdt=settings.DEFAULT_MARKUP_USDT)
wallet = WalletLedger(db_path=settings.DATABASE_PATH)

HTML_LANDING = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus Reseller Gateway</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0b0f19; color: #e5e7eb; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .card { background: #111827; border: 1px solid #1f2937; padding: 30px; border-radius: 16px; max-width: 480px; width: 100%; text-align: center; }
        .status { color: #10b981; font-weight: bold; margin-bottom: 10px; }
        h1 { margin: 0 0 10px 0; font-size: 24px; color: #fff; }
        p { color: #9ca3af; font-size: 14px; margin-bottom: 20px; }
        a { color: #3b82f6; text-decoration: none; font-weight: 600; }
    </style>
</head>
<body>
    <div class="card">
        <div class="status">🟢 SYSTEM ONLINE</div>
        <h1>Nexus Reseller Gateway</h1>
        <p>Anonymous Automated Reseller Engine & Crypto Gateway</p>
        <p><a href="/docs">API Documentation (/docs)</a> | <a href="/health">Health Status</a></p>
    </div>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def root_landing():
    return HTML_LANDING

@app.get("/health")
async def health_check():
    return {"status": "ok", "system": settings.SYSTEM_NAME, "version": settings.VERSION}

@app.get("/api/products")
async def list_products(markup_usdt: Optional[float] = None):
    return supplier.fetch_products(markup_usdt=markup_usdt)

@app.get("/api/balance")
async def supplier_balance():
    return supplier.fetch_balance()

@app.post("/api/order")
async def create_order(user_id: int = Body(...), product_id: int = Body(...), quantity: int = Body(1), retail_price_usdt: float = Body(...)):
    total = retail_price_usdt * quantity
    if not wallet.deduct_balance(user_id=user_id, amount_usdt=total, description=f"Product #{product_id}"):
        raise HTTPException(status_code=402, detail="Insufficient user wallet balance")
        
    res = supplier.execute_order(product_id=product_id, quantity=quantity)
    if not res.get("success"):
        wallet.credit_balance(user_id=user_id, amount_usdt=total, description="Refund")
        raise HTTPException(status_code=500, detail="Supplier error during fulfillment")
    return res

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"status": "error", "message": "Internal gateway error"})
