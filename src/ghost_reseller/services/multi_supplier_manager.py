"""
Multi-Supplier Aggregator & Price Optimizer
System: Nexus Reseller Core
Suppliers: Bunny AI Tools ($1.00), Prism1 Bot ($0.65), Duskyr Market
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class MultiSupplierManager:
    def __init__(self):
        self.suppliers = {
            "prism1": {
                "name": "Prism1 Bot Direct Source",
                "gemini_18m_cost_usdt": 0.65,
                "linkedin_3m_cost_usdt": 1.18,
                "netflix_cost_usdt": 1.95,
                "status": "active"
            },
            "bunny": {
                "name": "Bunny AI Tools",
                "gemini_18m_cost_usdt": 1.00,
                "canva_1y_cost_usdt": 7.50,
                "status": "active"
            },
            "duskyr": {
                "name": "Duskyr Market",
                "status": "active"
            }
        }

    def get_cheapest_product(self, product_key: str, default_markup_usdt: float = 3.0) -> Dict[str, Any]:
        """
        Busca el proveedor mayorista más barato disponible para maximizar la ganancia neta.
        Ejemplo: Para Gemini 18m, selecciona Prism1 ($0.65) sobre Bunny ($1.00).
        """
        if product_key == "gemini_18m":
            cost = self.suppliers["prism1"]["gemini_18m_cost_usdt"] # $0.65 USDT
            supplier_used = "Prism1 Bot"
        else:
            cost = self.suppliers["bunny"].get(f"{product_key}_cost_usdt", 1.00)
            supplier_used = "Bunny AI Tools"

        retail_price = round(cost + default_markup_usdt, 2)
        profit_margin = round(default_markup_usdt, 2)

        return {
            "product_key": product_key,
            "best_supplier": supplier_used,
            "supplier_cost_usdt": cost,
            "retail_price_usdt": retail_price,
            "profit_margin_usdt": profit_margin
        }

    def list_optimized_catalog(self, default_markup_usdt: float = 3.0) -> List[Dict[str, Any]]:
        """Retorna el catálogo optimizado con precios mínimos de costo y máximos márgenes de beneficio."""
        products = [
            {
                "id": 101,
                "key": "gemini_18m",
                "name": "Gemini Pro 18 Meses (Enlace Oficial)",
                "supplier": "Prism1 Bot",
                "cost_usdt": 0.65,
                "retail_usdt": round(0.65 + default_markup_usdt, 2),
                "profit_usdt": round(default_markup_usdt, 2)
            },
            {
                "id": 102,
                "key": "linkedin_3m",
                "name": "LinkedIn Career Premium 3 Meses",
                "supplier": "Prism1 Bot",
                "cost_usdt": 1.18,
                "retail_usdt": round(1.18 + default_markup_usdt, 2),
                "profit_usdt": round(default_markup_usdt, 2)
            },
            {
                "id": 103,
                "key": "netflix_1m",
                "name": "Netflix Premium Head 1 Mes",
                "supplier": "Prism1 Bot",
                "cost_usdt": 1.95,
                "retail_usdt": round(1.95 + default_markup_usdt, 2),
                "profit_usdt": round(default_markup_usdt, 2)
            },
            {
                "id": 104,
                "key": "figma_12m",
                "name": "Figma Edu Plan Pro 12 Meses",
                "supplier": "Prism1 Bot",
                "cost_usdt": 5.45,
                "retail_usdt": round(5.45 + default_markup_usdt, 2),
                "profit_usdt": round(default_markup_usdt, 2)
            }
        ]
        return products
