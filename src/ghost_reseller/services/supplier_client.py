"""
Supplier API Client
System: Nexus Reseller Core
"""

import requests
import os
from typing import Dict, Any, Optional

class SupplierClient:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://bhao.site/api/reseller/v1", default_markup_usdt: float = 3.0):
        self.api_key = api_key or os.getenv("RESELLER_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.default_markup_usdt = default_markup_usdt

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Nexus-Reseller-Gateway/1.0"
        }

    def fetch_products(self, markup_usdt: Optional[float] = None) -> Dict[str, Any]:
        if not self.api_key:
            return {"success": False, "error": "API Key not configured"}
            
        markup = markup_usdt if markup_usdt is not None else self.default_markup_usdt
        url = f"{self.base_url}/products"
        
        try:
            resp = requests.get(url, headers=self._get_headers(), timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                products = data.get("products", [])
                for p in products:
                    cost = float(p.get("your_cost", p.get("price_usdt", 0)))
                    p["supplier_cost_usdt"] = cost
                    p["retail_price_usdt"] = round(cost + markup, 2)
                    p["profit_margin_usdt"] = round(markup, 2)
                data["products"] = products
                return data
            else:
                return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def fetch_balance(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"success": False, "error": "API Key not configured"}
            
        url = f"{self.base_url}/balance"
        try:
            resp = requests.get(url, headers=self._get_headers(), timeout=10)
            if resp.status_code == 200:
                return resp.json()
            else:
                return {"success": False, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_order(self, product_id: int, quantity: int = 1, customer_email: Optional[str] = None) -> Dict[str, Any]:
        if not self.api_key:
            return {"success": False, "error": "API Key not configured"}
            
        url = f"{self.base_url}/order"
        payload = {"product_id": int(product_id), "quantity": int(quantity)}
        if customer_email:
            payload["customer_email"] = customer_email

        try:
            resp = requests.post(url, json=payload, headers=self._get_headers(), timeout=15)
            if resp.status_code in [200, 201]:
                return resp.json()
            else:
                return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
