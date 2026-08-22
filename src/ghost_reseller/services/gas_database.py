"""
Google Apps Script (GAS) Database Connector
System: Nexus Reseller Core
"""

import requests
import json
from typing import Dict, Any, Optional

class GASDatabaseConnector:
    def __init__(self, gas_webapp_url: Optional[str] = None):
        self.gas_webapp_url = gas_webapp_url

    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        if not self.gas_webapp_url:
            return {"balance_usdt": 0.0, "error": "GAS WebApp URL not configured"}
            
        url = f"{self.gas_webapp_url}?action=get_user&user_id={user_id}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            return {"balance_usdt": 0.0, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"balance_usdt": 0.0, "error": str(e)}

    def sync_user_balance(self, user_id: int, balance_usdt: float) -> Dict[str, Any]:
        if not self.gas_webapp_url:
            return {"success": False, "error": "GAS WebApp URL not configured"}
            
        payload = {
            "action": "update_balance",
            "user_id": user_id,
            "balance_usdt": balance_usdt
        }
        try:
            resp = requests.post(self.gas_webapp_url, json=payload, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            return {"success": False, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
